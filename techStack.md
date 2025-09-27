Tech Stack & Deployment
Component	Options	Notes
Orchestration	Python (FastAPI) / Node.js (NestJS)	Microservices architecture
Artifact Repo	PostgreSQL + S3/MinIO	Versioning + metadata
Messaging	WebSockets / gRPC / HTTP	A2A first, adapters later
Workflow UI	React + TypeScript	Drag-and-drop
Deployment	Docker + Kubernetes	Scalable, sandboxed
Security	OAuth2/JWT, encryption, sandboxing	Protect sensitive data
Key Principles 