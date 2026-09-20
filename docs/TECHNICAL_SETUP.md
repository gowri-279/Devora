DEVORA — Complete Technical Setup Guide

«This document provides a complete overview of the DEVORA architecture, technology stack, dependencies, environment configuration, and commands required to install and run the system from scratch.»

---

1. Project Architecture

DEVORA consists of five independently running application services, plus one MCP server process.

                         ┌─────────────────────┐
                         │   React Frontend    │
                         │      Port 3000      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Backend API      │
                         │      Port 8000      │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
       ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
       │ Knowledge Engine│ │ AI Integration  │ │Repository Parser│
       │    Port 8001    │ │    Port 8002    │ │    Port 8003    │
       └─────────────────┘ └─────────────────┘ └─────────────────┘
                 │                  │
                 └──────────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ MongoDB Atlas │
                    └───────────────┘

                    ┌───────────────┐
                    │   devora-mcp  │
                    │   MCP Server  │
                    └───────────────┘

The services are independently runnable. The startup order described later is a recommended order for convenience, not a strict dependency chain.

Responsibility Split

DEVORA separates project intelligence from developer intelligence.

Administrator

The administrator:

- Submits the project GitHub repository.
- Provides project documentation and knowledge sources.
- Initiates project/repository ingestion.
- Uses project-level analytics such as the Team Knowledge Heatmap.

Developer

The developer:

- Uploads their existing skill set/resume.
- Initializes their Developer Twin.
- Completes assessments.
- Follows the personalized learning path.
- Interacts with DEVORA and Bob during onboarding.

DEVORA

DEVORA combines:

Project Intelligence
        +
Developer Intelligence
        ↓
Developer Twin
        ↓
Personalized Project Onboarding

---

2. Core Components

2.1 Frontend

Technology: Vite + React + TypeScript

Port: "3000"

The frontend provides:

- Project onboarding interface
- Administrator repository/project submission
- Developer dashboard
- Developer Twin interface
- Skill-set/resume upload
- Personalized learning path
- Module learning and assessments
- Team Knowledge Heatmap
- Bob assistant interface
- Notifications and progress tracking

The frontend communicates only with the Backend API.

---

2.2 Backend API

Technology: FastAPI

Port: "8000"

The Backend acts as the main API gateway.

Responsibilities include:

- Frontend API handling
- Repository onboarding orchestration
- Communication with the Knowledge Engine
- Communication with AI Integration
- Communication with Repository Parser
- Developer Twin routes
- Learning-path requests
- Assessment-related operations
- Project and developer data coordination

---

2.3 Knowledge Engine

Technology: FastAPI + MongoDB Atlas + Sentence Transformers

Port: "8001"

The Knowledge Engine is the core intelligence and knowledge-processing layer.

Responsibilities include:

- Document ingestion
- Text extraction
- Text chunking
- Embedding generation
- Semantic search
- MongoDB Atlas Vector Search
- Knowledge-gap identification
- Learning-path generation
- Module quizzes
- Learning progress
- Developer Twin data
- Knowledge retrieval for Bob

Embedding Model

all-MiniLM-L6-v2

Embedding dimension:

384

Vector similarity:

Cosine similarity

MongoDB Atlas Vector Search index:

vector_index

Vector field:

embedding

---

2.4 AI Integration

Technology: FastAPI + IBM Bob integration

Port: "8002"

The AI Integration service handles AI-powered functionality including:

- IBM Bob interaction
- Grounded question answering
- Assessment evaluation
- Curriculum generation
- AI-assisted learning content generation

DEVORA supports both live and mock Bob modes.

DEVORA_BOB_MODE=mock

or:

DEVORA_BOB_MODE=live

---

2.5 Repository Parser

Technology: Python + GitPython + API service

Port: "8003"

The Repository Parser analyzes project repositories submitted by the administrator.

It extracts repository intelligence such as:

- Repository structure
- Source files
- Project artifacts
- Code-related information
- Project metadata

The extracted repository intelligence is passed into DEVORA's knowledge pipeline.

Dependencies

Dependencies are declared in:

repository-parser/requirements.txt

"GitPython" is currently listed for repository analysis.

---

2.6 DEVORA MCP Server

DEVORA includes an MCP server called:

devora-mcp

It exposes DEVORA knowledge retrieval capabilities to MCP-compatible environments.

Primary tool:

search_devora_knowledge

The MCP server allows external MCP-compatible AI environments to retrieve relevant DEVORA knowledge through the semantic knowledge layer.

---

3. Technology Stack

Layer| Technology
Frontend| React + TypeScript + Vite
Backend| FastAPI
Knowledge Engine| FastAPI + Sentence Transformers
AI Integration| FastAPI + IBM Bob
Repository Parser| Python + GitPython
Database| MongoDB Atlas
Vector Search| MongoDB Atlas Vector Search
Embeddings| all-MiniLM-L6-v2
MCP| Model Context Protocol
Document Parsing| PyPDF + python-docx
Text Splitting| LangChain Text Splitters
Repository Analysis| GitPython

---

4. Data Flow

4.1 Project Repository Onboarding

The administrator submits the project GitHub repository.

Admin
  │
  ▼
Project GitHub Repository
  │
  ▼
Backend API :8000
  │
  ▼
Repository Parser :8003
  │
  ▼
Repository Intelligence
  │
  ▼
Knowledge Engine :8001
  │
  ├── Document Processing
  ├── Chunking
  ├── Embeddings
  └── Vector Storage
  │
  ▼
Project Knowledge Base
  │
  ▼
Personalized Learning Path

---

5. Developer Twin Flow

The Developer Twin is initialized from the developer's existing skill set.

Developer Skill Set / Resume
            │
            ▼
      Skill Extraction
            │
            ▼
    Initial Skill Profile
            │
            ▼
      Developer Twin
            │
            ├── Repository Intelligence
            ├── Assessment Results
            ├── Knowledge Gaps
            └── Learning Progress

The Developer Twin evolves as the developer progresses through onboarding.

---

6. Personalized Learning Path

DEVORA generates a personalized learning path by combining developer intelligence with project intelligence.

Developer Skill Profile
          +
Developer Twin
          +
Repository Intelligence
          +
Project Knowledge
          +
Knowledge Gaps
          ↓
Personalized Learning Path

This allows DEVORA to identify what the developer already knows and what they need to learn specifically for the target project.

---

7. Ask Bob Flow

Developer Question
        │
        ▼
Frontend
        │
        ▼
Backend
        │
        ▼
Knowledge Retrieval
        │
        ▼
Relevant Project Knowledge
        │
        ▼
IBM Bob
        │
        ▼
Grounded Answer

Bob is designed to answer questions using relevant DEVORA project knowledge rather than relying only on generic model knowledge.

---

8. Assessment Flow

Developer
    │
    ▼
Assessment
    │
    ▼
Answer Submission
    │
    ▼
AI Evaluation
    │
    ▼
Assessment Results
    │
    ▼
Knowledge Gaps
    │
    ▼
Developer Twin Update
    │
    ▼
Learning Path Update

Assessment results contribute to the evolving Developer Twin and personalized learning experience.

---

9. MongoDB Atlas

Database:

devora

Core collections include:

Collection| Purpose
"knowledge_chunks"| Chunked project/document knowledge and embeddings
"raw_documents"| Original ingested document information
"projects_meta"| Project metadata
"knowledge_gaps"| Identified knowledge gaps
"developer_twins"| Developer Twin information
"module_progress"| Developer learning progress
"assessments"| Assessment data and results
"projects"| Project information
"notifications"| Developer notifications
"users"| User information
"teams"| Team information

---

10. MongoDB Vector Search

The "knowledge_chunks" collection uses MongoDB Atlas Vector Search.

Configuration:

Index: vector_index
Field: embedding
Dimensions: 384
Similarity: cosine
Model: all-MiniLM-L6-v2

DEVORA can also use an in-memory cosine-similarity fallback when required.

---

11. API Endpoints

Backend — Port 8000

Endpoint| Purpose
"POST /api/upload/repository"| Admin submits a project GitHub repository for analysis and ingestion
"GET /api/learning-path"| Retrieves/generates a personalized learning path
"/api/developer-twin/..."| Developer Twin operations
"/api/assessment/..."| Assessment operations
"/api/projects/..."| Project operations
"/api/notifications/..."| Notification operations

«Endpoint groups represented with "..." indicate route families rather than a single endpoint.»

---

Knowledge Engine — Port 8001

The Knowledge Engine provides APIs for:

- Knowledge ingestion
- Semantic search
- Learning-path generation
- Module quizzes
- Knowledge-gap handling
- Developer Twin data
- Progress tracking

Representative modules include:

ingest_api.py
generate_learning_path.py
module_quiz.py

---

AI Integration — Port 8002

The AI Integration service provides APIs for:

- Bob interaction
- Curriculum generation
- Assessment evaluation
- AI-assisted responses

Important service:

curriculum_service.py

---

Repository Parser — Port 8003

Representative endpoints:

GET /
POST /repositories/analyse
GET /artifacts/{artifact_id}

---

12. Environment Variables

Create a root ".env" file containing values appropriate for the deployment environment.

Example:

MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=devora
MONGODB_COLLECTION=knowledge_chunks

KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001
AI_INTEGRATION_URL=http://127.0.0.1:8002
REPOSITORY_PARSER_URL=http://127.0.0.1:8003

DEVORA_AI_INTEGRATION_URL=http://127.0.0.1:8002
DEVORA_BACKEND_URL=http://127.0.0.1:8000

BOB_API_KEY=<your-key>
DEVORA_BOB_MODE=mock

VITE_DEVORA_API_URL=http://127.0.0.1:8000/api

Do not commit real credentials, API keys, or MongoDB credentials to GitHub.

---

13. Frontend Environment

The frontend uses:

VITE_DEVORA_API_URL=http://127.0.0.1:8000/api

This ensures that frontend requests are routed through the Backend API.

---

14. Installation

14.1 Clone the Repository

git clone <repository-url>
cd <repository-folder>

---

14.2 Configure Environment

Linux/macOS:

cp .env.example .env

Windows PowerShell:

Copy-Item .env.example .env

Update the ".env" values as required.

---

15. Backend Setup

Navigate to the backend:

cd backend

Create/activate a virtual environment:

python -m venv venv

Linux/macOS:

source venv/bin/activate

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run:

uvicorn app.main:app --reload --port 8000

---

16. Knowledge Engine Setup

cd knowledge-engine

Create/activate the Python environment and install dependencies:

pip install -r requirements.txt

Run:

uvicorn app.main:app --reload --port 8001

---

17. AI Integration Setup

cd ai-integration

Install dependencies:

pip install -r requirements.txt

Run:

uvicorn app.main:app --reload --port 8002

AI Integration Dependencies

The service currently specifies:

fastapi==0.115.12
uvicorn==0.34.3
pydantic==2.11.4
python-dotenv==1.1.0
mcp==1.9.4
httpx==0.28.1
pytest==8.3.5

---

18. Repository Parser Setup

cd repository-parser

Install the dependencies listed in:

requirements.txt

For example:

pip install -r requirements.txt

Run the service according to the API entry point defined in the Repository Parser implementation.

The repository parser uses "GitPython" for repository analysis.

---

19. Frontend Setup

Navigate to:

cd frontend/client

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend runs on:

http://localhost:3000

---

20. Recommended Startup Order

The services can be started independently. For a complete local run, the following order is recommended:

1. Repository Parser     :8003
2. AI Integration        :8002
3. Knowledge Engine      :8001
4. Backend API           :8000
5. Frontend              :3000

Again, this is a convenient startup sequence rather than a strict service dependency chain.

---

21. Frontend API Architecture

DEVORA follows a controlled frontend-to-backend communication model.

React Frontend
      │
      │ HTTP
      ▼
Backend API :8000
      │
      ├──────────► Knowledge Engine :8001
      │
      ├──────────► AI Integration :8002
      │
      └──────────► Repository Parser :8003

The frontend does not directly communicate with the internal services.

---

22. Knowledge Ingestion Pipeline

Project Repository / Documents
             │
             ▼
      Document Extraction
             │
             ▼
          Chunking
             │
             ▼
        Embeddings
             │
             ▼
      MongoDB Atlas
             │
             ▼
      Vector Search
             │
             ▼
      Relevant Knowledge

Supported document processing includes:

- PDF
- DOCX
- Text-based project artifacts
- Repository source files

---

23. Developer Onboarding Pipeline

Developer
    │
    ▼
Upload Skill Set / Resume
    │
    ▼
Skill Extraction
    │
    ▼
Initial Skill Profile
    │
    ▼
Developer Twin
    │
    ▼
Project Assessment
    │
    ▼
Knowledge Gaps
    │
    ▼
Personalized Learning Path
    │
    ▼
Learning Modules
    │
    ▼
Quizzes / Assessments
    │
    ▼
Developer Twin Updates

---

24. Project Onboarding Pipeline

Admin
  │
  ▼
Project GitHub Repository
  │
  ▼
Repository Parser
  │
  ▼
Repository Intelligence
  │
  ▼
Knowledge Engine
  │
  ▼
Project Knowledge Base
  │
  ▼
Developer + Project Context
  │
  ▼
Personalized Onboarding

---

25. Team Knowledge Heatmap

The Team Knowledge Heatmap provides an administrator-level view of team knowledge across project-relevant domains.

Example domains include:

APIs
Architecture
Database
Security

The Heatmap is intended to help identify:

- Team-wide knowledge gaps
- Individual skill gaps
- Areas requiring additional onboarding
- Knowledge distribution across the team

Some frontend visualization/presentation data may still use mock/demo values depending on the current UI implementation.

---

26. IBM Bob Integration

DEVORA integrates IBM Bob into the onboarding experience.

Bob supports:

- Contextual project questions
- Knowledge-grounded responses
- Assessment evaluation
- Curriculum generation
- Learning assistance

DEVORA can run in:

Mock Mode

DEVORA_BOB_MODE=mock

This allows development and demonstrations without a live Bob integration.

Live Mode

DEVORA_BOB_MODE=live

This uses the configured Bob integration and requires:

BOB_API_KEY=<your-key>

---

27. MCP Integration

DEVORA includes an MCP server for exposing its knowledge retrieval capabilities.

Primary MCP tool:

search_devora_knowledge

Conceptually:

MCP Client
    │
    ▼
devora-mcp
    │
    ▼
DEVORA Knowledge Retrieval
    │
    ▼
Relevant Project Knowledge

This enables MCP-compatible AI systems to access project-specific DEVORA knowledge.

---

28. Frontend API Layer

The frontend centralizes API communication through its DEVORA API layer.

Important file:

frontend/client/src/lib/devoraApi.ts

This layer handles communication between the frontend and Backend API.

Mock/demo data is maintained separately where required.

Important file:

frontend/client/src/lib/devoraMockData.ts

---

29. Current Implementation Status

Feature| Status
Project repository ingestion| Implemented
Repository intelligence extraction| Implemented
Knowledge ingestion| Implemented
MongoDB Atlas integration| Implemented
Vector Search| Implemented
Semantic knowledge search| Implemented
Personalized learning path| Implemented
Developer skill-set/resume initialization| Implemented
Skill extraction| Implemented
Developer Twin initialization| Implemented
Assessment system| Implemented
Assessment evaluation| Implemented
Knowledge-gap identification| Implemented
Learning modules| Implemented
Module quizzes| Implemented
Learning progress tracking| Implemented
Notifications| Implemented
IBM Bob integration| Implemented with mock/live modes
MCP knowledge retrieval| Implemented
Team Knowledge Heatmap| Partially integrated
Admin automatic "Implement Module" action| Future enhancement

---

30. Known Issues / Limitations

Area| Status / Note
AI Integration requirements| Encoding/dependency issue addressed
Frontend API port| Previously corrected from "8001" to Backend "8000"
MCP backend port| Port mismatch corrected
MCP server| Indentation issue corrected
Notifications| Database function issue corrected
Backend Bob integration| Placeholder implementation corrected
Bob availability| Mock fallback added
Root ".env.example"| Added/configured
Frontend ".env.example"| Added
Developer Twin skill-set initialization| Implemented
Developer Twin frontend presentation| Some mock/demo fallback logic may remain
Team Heatmap frontend| Some mock/demo presentation data may remain
Admin automatic module implementation| Future enhancement

---

31. Important Project Files

File| Purpose
"README.md"| Project overview and setup
"ai-integration/app/services/curriculum_service.py"| Curriculum generation
"backend/app/routes/twin.py"| Developer Twin routes
"backend/app/services/knowledge_engine.py"| Backend ↔ Knowledge Engine communication
"frontend/client/src/lib/devoraApi.ts"| Frontend API layer
"frontend/client/src/lib/devoraMockData.ts"| Frontend mock/demo data
"frontend/client/src/pages/Home.tsx"| Main frontend page
"knowledge-engine/app/generate_learning_path.py"| Learning-path generation
"knowledge-engine/app/ingest_api.py"| Knowledge ingestion
"knowledge-engine/app/module_quiz.py"| Module quiz functionality

---

32. Troubleshooting

Backend Cannot Connect to Knowledge Engine

Check:

KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001

Ensure the Knowledge Engine is running on port "8001".

---

Backend Cannot Connect to AI Integration

Check:

AI_INTEGRATION_URL=http://127.0.0.1:8002

Ensure AI Integration is running on port "8002".

---

Repository Analysis Fails

Check:

REPOSITORY_PARSER_URL=http://127.0.0.1:8003

Ensure Repository Parser is running on port "8003".

Also verify that the submitted repository URL is accessible.

---

Frontend Cannot Reach Backend

Check:

VITE_DEVORA_API_URL=http://127.0.0.1:8000/api

Ensure the Backend API is running on port "8000".

---

Bob Is Unavailable

Use mock mode:

DEVORA_BOB_MODE=mock

This allows the system to operate without a live Bob API connection.

---

MongoDB Connection Problems

Verify:

MONGODB_URI=<valid MongoDB Atlas connection string>
MONGODB_DATABASE=devora

Also ensure the MongoDB Atlas deployment allows the machine's network connection.

---

33. Master Technical Context

DEVORA is a five-service Python + TypeScript developer onboarding platform with an MCP server.

The architecture is:

Frontend :3000
     ↓
Backend :8000
     ↓
 ┌───┼────────────┐
 ↓   ↓            ↓
KE  AI          Parser
8001 8002         8003

The frontend communicates only with the Backend.

The Knowledge Engine uses:

all-MiniLM-L6-v2
384-dimensional embeddings
MongoDB Atlas Vector Search
Cosine similarity

DEVORA's knowledge sources include:

- Project documentation
- Project repository source code submitted by the Administrator
- Uploaded project documents
- Developer skill sets/resumes
- Assessment results
- Learning activity

The Developer Twin follows:

Developer Skill Set / Resume
          ↓
Profile Ingestion
          ↓
Skill Extraction
          ↓
Initial Skill Profile
          ↓
Developer Twin

The Twin can incorporate:

Repository Intelligence
Assessment Results
Knowledge Gaps
Learning Progress

The personalized learning path combines:

Developer Skill Profile
Developer Twin
Repository Intelligence
Project Knowledge
Knowledge Gaps

IBM Bob provides:

Grounded Q&A
Assessment Evaluation
Curriculum Generation

Bob supports:

DEVORA_BOB_MODE=mock

for demonstration/development and:

DEVORA_BOB_MODE=live

for live integration.

The frontend API layer centralizes communication through the Backend.

Mock/demo data remains present in selected frontend presentation areas where required for demonstration and fallback behavior.

---

34. Final System Flow

                         ADMIN
                           │
                           ▼
                Project GitHub Repository
                           │
                           ▼
                  Repository Parser
                           │
                           ▼
                Repository Intelligence
                           │
                           ▼
                    Knowledge Engine
                           │
                           ▼
                   Project Knowledge
                           │
                           │
                           ▼
DEVELOPER ──► Skill Set / Resume
                           │
                           ▼
                   Skill Extraction
                           │
                           ▼
                   Developer Twin
                           │
                           ├───────────────┐
                           │               │
                           ▼               ▼
                    Assessment       Project Context
                           │               │
                           └───────┬───────┘
                                   ▼
                           Knowledge Gaps
                                   │
                                   ▼
                     Personalized Learning Path
                                   │
                                   ▼
                          Learning Modules
                                   │
                                   ▼
                            Assessments
                                   │
                                   ▼
                       Developer Twin Updates
                                   │
                                   ▼
                           IBM Bob Assistance

DEVORA therefore combines project intelligence with developer intelligence to create a personalized, project-aware onboarding experience rather than providing a generic learning platform.
