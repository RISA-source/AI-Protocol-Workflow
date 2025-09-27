"""
Artifact repository implementation with lineage tracking
"""

import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import os

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from app.models.artifacts import Artifact, ArtifactDependency, ContentCategory, StorageType, ValidationStatus, DependencyType
from app.core.config import settings
from app.core.database import get_db

class ArtifactRepository:
    """
    Repository for managing artifacts with lineage tracking
    """
    
    def __init__(self):
        self.base_path = Path(settings.ARTIFACT_BASE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    @asynccontextmanager
    async def get_db_session(self):
        """
        Async context manager to yield DB session
        """
        async for session in get_db():
            yield session
    
    async def create_artifact(self, 
                             source_agent_id: str,
                             workflow_id: uuid.UUID,
                             task_id: uuid.UUID,
                             content: Any,
                             content_type: str,
                             parent_artifact_ids: List[uuid.UUID] = None,
                             metadata: Dict[str, Any] = None) -> uuid.UUID:
        """
        Create new artifact and return its ID
        """
        async with self.get_db_session() as session:
            artifact_id = uuid.uuid4()
            
            # Determine content category and storage
            content_category = self._determine_category(content_type)
            storage_type, storage_path, content_text = self._prepare_storage(content, content_type)
            
            # Calculate size
            size_bytes = len(str(content).encode('utf-8')) if isinstance(content, str) else 0
            
            # Create artifact record
            artifact = Artifact(
                artifact_id=artifact_id,
                parent_artifact_ids=parent_artifact_ids or [],
                source_agent_id=source_agent_id,
                workflow_id=workflow_id,
                task_id=task_id,
                content_type=content_type,
                content_category=content_category,
                storage_type=storage_type,
                storage_path=storage_path,
                content_text=content_text,
                custom_metadata=metadata or {},
                size_bytes=size_bytes
            )
            
            session.add(artifact)
            await session.flush()
            
            # Create dependency relationships
            if parent_artifact_ids:
                await self._create_dependencies(session, artifact_id, parent_artifact_ids, DependencyType.DIRECT_INPUT)
            
            await session.commit()
            return artifact_id
    
    async def get_artifact(self, artifact_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve artifact by ID with content
        """
        async with self.get_db_session() as session:
            stmt = select(Artifact).where(Artifact.artifact_id == artifact_id)
            result = await session.execute(stmt)
            artifact = result.scalar_one_or_none()
            
            if not artifact:
                return None
            
            # Load content based on storage type
            content = None
            if artifact.storage_type == StorageType.INLINE:
                content = artifact.content_text
            elif artifact.storage_type == StorageType.FILESYSTEM:
                content = self._load_from_file(artifact.storage_path)
            
            return {
                "artifact_id": str(artifact.artifact_id),
                "parent_artifact_ids": [str(pid) for pid in artifact.parent_artifact_ids],
                "source_agent_id": artifact.source_agent_id,
                "workflow_id": str(artifact.workflow_id),
                "task_id": str(artifact.task_id),
                "content_type": artifact.content_type,
                "content_category": artifact.content_category.value,
                "storage_type": artifact.storage_type.value,
                "content": content,
                "title": artifact.title,
                "description": artifact.description,
                "tags": artifact.tags,
                "custom_metadata": artifact.custom_metadata,
                "validation_status": artifact.validation_status.value,
                "validation_details": artifact.validation_details,
                "confidence_score": artifact.confidence_score,
                "created_at": artifact.created_at.isoformat(),
                "version": artifact.version,
                "size_bytes": artifact.size_bytes
            }
    
    async def get_lineage(self, artifact_id: uuid.UUID, direction: str = 'both') -> Dict[str, List[Dict[str, Any]]]:
        """
        Get artifact lineage - parents (inputs) and/or children (outputs)
        """
        async with self.get_db_session() as session:
            lineage = {'parents': [], 'children': []}
            
            if direction in ['both', 'parents']:
                # Get parent artifacts
                stmt = select(ArtifactDependency, Artifact).join(
                    Artifact, ArtifactDependency.parent_artifact_id == Artifact.artifact_id
                ).where(ArtifactDependency.child_artifact_id == artifact_id)
                
                result = await session.execute(stmt)
                for dep, artifact in result:
                    lineage['parents'].append({
                        'id': str(artifact.artifact_id),
                        'type': dep.dependency_type.value,
                        'title': artifact.title,
                        'content_type': artifact.content_type
                    })
            
            if direction in ['both', 'children']:
                # Get child artifacts
                stmt = select(ArtifactDependency, Artifact).join(
                    Artifact, ArtifactDependency.child_artifact_id == Artifact.artifact_id
                ).where(ArtifactDependency.parent_artifact_id == artifact_id)
                
                result = await session.execute(stmt)
                for dep, artifact in result:
                    lineage['children'].append({
                        'id': str(artifact.artifact_id),
                        'type': dep.dependency_type.value,
                        'title': artifact.title,
                        'content_type': artifact.content_type
                    })
            
            return lineage
    
    async def get_workflow_artifacts(self, workflow_id: uuid.UUID, order_by: str = 'created_at') -> List[Dict[str, Any]]:
        """
        Get all artifacts for a workflow
        """
        async with self.get_db_session() as session:
            stmt = select(Artifact).where(Artifact.workflow_id == workflow_id)
            
            if order_by == 'created_at':
                stmt = stmt.order_by(Artifact.created_at)
            
            result = await session.execute(stmt)
            artifacts = result.scalars().all()
            
            return [self._serialize_artifact(a) for a in artifacts]

    async def update_validation_status(self, artifact_id: uuid.UUID, status: ValidationStatus, details: Dict[str, Any]):
        """
        Update artifact validation status
        """
        async with self.get_db_session() as session:
            stmt = select(Artifact).where(Artifact.artifact_id == artifact_id)
            result = await session.execute(stmt)
            artifact = result.scalar_one_or_none()
            
            if artifact:
                artifact.validation_status = status
                artifact.validation_details = details
                await session.commit()
    
    def _determine_category(self, content_type: str) -> ContentCategory:
        """Determine content category from MIME type"""
        if content_type.startswith('text/'):
            return ContentCategory.TEXT
        elif content_type == 'application/json':
            return ContentCategory.DATA
        elif content_type.startswith('image/'):
            return ContentCategory.IMAGE
        elif content_type in ['application/pdf', 'application/msword']:
            return ContentCategory.DOCUMENT
        else:
            return ContentCategory.BINARY
    
    def _prepare_storage(self, content: Any, content_type: str) -> tuple:
        """Determine how and where to store artifact content"""
        # Inline storage for small text content
        if content_type.startswith('text/') and len(str(content)) < settings.MAX_INLINE_SIZE:
            return StorageType.INLINE, None, str(content)
        
        # Filesystem storage for development
        if content_type.startswith('text/') or content_type == 'application/json':
            file_path = self._save_to_file(content, content_type)
            return StorageType.FILESYSTEM, file_path, None
        
        # Binary content always goes to filesystem
        file_path = self._save_binary_to_file(content, content_type)
        return StorageType.FILESYSTEM, file_path, None
    
    def _save_to_file(self, content: Any, content_type: str) -> str:
        """Save content to local filesystem"""
        today = datetime.now()
        dir_path = self.base_path / f"{today.year:04d}" / f"{today.month:02d}" / f"{today.day:02d}"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        artifact_uuid = str(uuid.uuid4())
        extension = self._get_file_extension(content_type)
        file_path = dir_path / f"{artifact_uuid}{extension}"
        
        if isinstance(content, str):
            file_path.write_text(content, encoding='utf-8')
        else:
            file_path.write_bytes(content)
        
        return str(file_path.relative_to(self.base_path))
    
    def _save_binary_to_file(self, content: Any, content_type: str) -> str:
        """Save binary content to filesystem"""
        return self._save_to_file(content, content_type)
    
    def _load_from_file(self, storage_path: str) -> str:
        """Load content from filesystem"""
        file_path = self.base_path / storage_path
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        return ""
    
    def _get_file_extension(self, content_type: str) -> str:
        """Get file extension from content type"""
        extensions = {
            'text/plain': '.txt',
            'text/markdown': '.md',
            'application/json': '.json',
            'application/pdf': '.pdf',
            'image/png': '.png',
            'image/jpeg': '.jpg'
        }
        return extensions.get(content_type, '.bin')
    
    async def _create_dependencies(self, session: AsyncSession, child_id: uuid.UUID, parent_ids: List[uuid.UUID], dep_type: DependencyType):
        """Create dependency relationships"""
        for parent_id in parent_ids:
            dependency = ArtifactDependency(
                child_artifact_id=child_id,
                parent_artifact_id=parent_id,
                dependency_type=dep_type
            )
            session.add(dependency)

    def _serialize_artifact(self, artifact: Artifact) -> Dict[str, Any]:
        """Helper to serialize artifact object"""
        content = None
        if artifact.storage_type == StorageType.INLINE:
            content = artifact.content_text
        elif artifact.storage_type == StorageType.FILESYSTEM:
            content = self._load_from_file(artifact.storage_path)
        return {
            "artifact_id": str(artifact.artifact_id),
            "source_agent_id": artifact.source_agent_id,
            "content_type": artifact.content_type,
            "content_category": artifact.content_category.value,
            "title": artifact.title,
            "description": artifact.description,
            "validation_status": artifact.validation_status.value,
            "created_at": artifact.created_at.isoformat(),
            "size_bytes": artifact.size_bytes,
            "content": content
        }
