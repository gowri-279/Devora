# DEVORA — Complete Technical Setup Guide

> Complete technical documentation for DEVORA, including its architecture, technology stack, service structure, APIs, database design, environment configuration, installation, runtime workflows, Developer Twin initialization, and current implementation status.

---

## 1. Project Architecture

DEVORA consists of **five independently running services** communicating over HTTP, plus one MCP server process.

```text
┌─────────────────────────────────────────────────────────┐
│                     Browser / User                      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP :3000
┌──────────────────────▼──────────────────────────────────┐
│            Frontend — Vite + React + TypeScript         │
│                       :3000                             │
└──────────────────────┬──────────────────────────────────┘
                       │ REST /api/*
                       │ :8000
┌──────────────────────▼──────────────────────────────────┐
│              Backend API — FastAPI :8000                │
│                    Main API Gateway                     │
└──────┬───────────────────┬───────────────────┬──────────┘
       │ :8001             │ :8002             │ :8003
┌──────▼─────────┐  ┌──────▼──────────┐  ┌─────▼──────────┐
│ Knowledge      │  │ AI Integration  │  │ Repository     │
│ Engine         │  │ IBM Bob         │  │ Parser         │
│ :8001          │  │ :8002           │  │ :8003          │
└──────┬─────────┘  └──────┬──────────┘  └────────────────┘
       │                   │
       ▼                   ▼
 MongoDB Atlas          IBM Bob CLI
 Vector Search          (`bob run`)
```

### Communication Pattern

```text
Frontend
   │
   ▼
Backend API
   │
   ├──► Knowledge Engine
   │
   ├──► AI Integration ──► IBM Bob
   │
   └──► Repository Parser
```

The **frontend communicates only with the Backend API**.

The Backend acts as the primary API gateway and coordinates the Knowledge Engine, AI Integration service, and Repository Parser.

The Knowledge Engine can communicate with AI Integration for curriculum generation.

---

# 2. Complete Technology Stack

| Layer               | Technology                  | Version / Details  |
| ------------------- | --------------------------- | ------------------ |
| Frontend framework  | React                       | 19.x               |
| Frontend build tool | Vite                        | 7.x                |
| Frontend language   | TypeScript                  | 5.6.3              |
| Frontend CSS        | TailwindCSS                 | 4.x                |
| UI components       | shadcn/ui / Radix UI        | Latest             |
| Routing             | Wouter                      | 3.3.5              |
| Animations          | Framer Motion               | 12.x               |
| Charts              | Recharts                    | 2.15.x             |
| HTTP                | Fetch / Axios               | Native + Axios     |
| Package manager     | pnpm                        | 10.4.1             |
| Backend framework   | FastAPI                     | Latest             |
| Backend server      | Uvicorn                     | Latest             |
| Backend language    | Python                      | 3.10+              |
| Knowledge Engine    | FastAPI                     | Latest             |
| Embeddings          | SentenceTransformers        | `all-MiniLM-L6-v2` |
| Vector store        | MongoDB Atlas Vector Search | Cloud              |
| Database            | MongoDB Atlas               | Cloud              |
| MongoDB driver      | PyMongo                     | Latest             |
| PDF parsing         | PyPDF                       | Latest             |
| DOCX parsing        | python-docx                 | Latest             |
| Text splitting      | LangChain Text Splitters    | Latest             |
| Repository cloning  | GitPython                   | Latest             |
| AI Integration      | FastAPI                     | 0.115.x            |
| AI invocation       | IBM Bob CLI                 | `bob run`          |
| MCP server          | MCP Python SDK              | 1.9.x              |

---

# 3. Directory Structure

```text
Devora/
│
├── .env.example
├── .env
├── README.md
│
├── frontend/
│   ├── client/
│   │   └── src/
│   │       ├── App.tsx
│   │       ├── pages/
│   │       │   └── Home.tsx
│   │       ├── components/
│   │       │   ├── BobAssistant
│   │       │   ├── DeveloperTwin
│   │       │   ├── TeamKnowledgeHeatmap
│   │       │   └── ...
│   │       └── lib/
│   │           ├── devoraApi.ts
│   │           └── devoraMockData.ts
│   │
│   ├── server/
│   │   └── index.ts
│   ├── vite.config.ts
│   ├── package.json
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database/
│   │   │   └── mongodb.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── learning.py
│   │   │   ├── upload.py
│   │   │   ├── bob.py
│   │   │   ├── assessment.py
│   │   │   ├── twin.py
│   │   │   ├── gaps.py
│   │   │   └── notifications.py
│   │   └── services/
│   │       ├── knowledge_engine.py
│   │       ├── ai_integration.py
│   │       ├── project.py
│   │       └── assessment.py
│   │
│   └── requirements.txt
│
├── knowledge-engine/
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── search.py
│   │   ├── embeddings.py
│   │   ├── ingest_core.py
│   │   ├── ingest_api.py
│   │   ├── generate_learning_path.py
│   │   ├── developer_twin.py
│   │   ├── assessment.py
│   │   ├── gap_tracker.py
│   │   └── module_quiz.py
│   │
│   └── requirements.txt
│
├── ai-integration/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   │   └── bob.py
│   │   └── services/
│   │       ├── ibm_bob_client.py
│   │       ├── bob_service.py
│   │       ├── assessment_evaluator.py
│   │       ├── assessment_prompt.py
│   │       └── curriculum_service.py
│   │
│   └── requirements.txt
│
├── repository-parser/
│   ├── api.py
│   ├── parser.py
│   ├── scanner.py
│   ├── language_detector.py
│   ├── module_detector.py
│   ├── dependency_detector.py
│   ├── symbol_detector.py
│   ├── entrypoint_detector.py
│   ├── tech_stack_detector.py
│   ├── github_clone.py
│   ├── zip_handler.py
│   └── requirements.txt
│
└── devora-mcp/
    ├── server.py
    └── test_client.py
```

---

# 4. Core Components

## 4.1 Frontend

The React frontend provides:

* Developer dashboard
* Project onboarding
* Repository submission
* Knowledge exploration
* Bob Assistant
* Developer Twin
* Skill-set / resume upload
* Initial skill assessment
* Personalized learning path
* Module progression
* Module quizzes
* Knowledge gaps
* Notifications
* Team knowledge visualization
* Admin-oriented project intelligence

The frontend API layer is centralized in:

```text
frontend/client/src/lib/devoraApi.ts
```

---

## 4.2 Backend API

The Backend is the **main gateway** between the frontend and DEVORA's internal services.

Responsibilities include:

* Authentication
* Project management
* Repository upload orchestration
* Document upload
* Developer Twin operations
* Skill-set / resume processing orchestration
* Assessment orchestration
* Learning-path requests
* Bob requests
* Notifications
* Knowledge-gap operations
* Module progress

---

## 4.3 Knowledge Engine

The Knowledge Engine is DEVORA's **data and intelligence core**.

It handles:

* Document ingestion
* Repository knowledge ingestion
* Resume / skill-set ingestion
* Skill extraction
* Semantic search
* Embedding generation
* Vector retrieval
* Developer Twin storage
* Skill-gap detection
* Learning-path generation
* Module quizzes
* Assessment-related knowledge retrieval

The embedding model is:

```text
all-MiniLM-L6-v2
```

It produces:

```text
384-dimensional vectors
```

which are stored in MongoDB Atlas Vector Search.

---

## 4.4 AI Integration

The AI Integration service provides the interface between DEVORA and IBM Bob.

IBM Bob is used for:

* Grounded developer Q&A
* Assessment evaluation
* Curriculum generation
* Personalized learning-path generation

IBM Bob is invoked through:

```text
bob run
```

The service also supports a deterministic mock mode for environments where IBM Bob is unavailable.

---

## 4.5 Repository Parser

The Repository Parser analyzes developer repositories and extracts project intelligence.

It detects:

* Programming languages
* Modules
* Dependencies
* Symbols
* Entry points
* Technology stack
* Repository structure

The resulting repository intelligence is passed to the Knowledge Engine and learning-path generation pipeline.

---

## 4.6 MCP Server

The `devora-mcp` server exposes DEVORA knowledge to IBM Bob through MCP.

Primary tool:

```text
search_devora_knowledge
```

This enables Bob to interact with DEVORA's knowledge layer when MCP is configured.

---

# 5. Backend API Endpoints

The Backend runs on:

```text
http://127.0.0.1:8000
```

## Authentication / Dashboard

| Method | Path         | Description             |
| ------ | ------------ | ----------------------- |
| POST   | `/register`  | Register a user         |
| POST   | `/login`     | Authenticate a user     |
| GET    | `/dashboard` | Retrieve dashboard data |

## Learning

| Method | Path                 | Description                                       |
| ------ | -------------------- | ------------------------------------------------- |
| POST   | `/api/learning-path` | Generate or retrieve a personalized learning path |

## Repository / Documents

| Method | Path                            | Description                            |
| ------ | ------------------------------- | -------------------------------------- |
| POST   | `/api/upload/repository`        | Analyze and ingest a GitHub repository |
| POST   | `/api/upload/documents`         | Upload a project document              |
| GET    | `/api/documents`                | List project documents                 |
| GET    | `/api/projects/{id}/repository` | Retrieve repository information        |

## Bob

| Method | Path           | Description                    |
| ------ | -------------- | ------------------------------ |
| POST   | `/api/ask-bob` | Ask a grounded question to Bob |

## Assessment

| Method | Path                           | Description                              |
| ------ | ------------------------------ | ---------------------------------------- |
| POST   | `/api/assessments`             | Create an assessment                     |
| POST   | `/api/assessments/{id}/submit` | Submit assessment and trigger evaluation |

## Developer Twin

| Method | Path                                 | Description                                       |
| ------ | ------------------------------------ | ------------------------------------------------- |
| GET    | `/api/developer-twin/{developer_id}` | Retrieve a Developer Twin                         |
| POST   | `/api/developer-twin/...`            | Developer Twin initialization / update operations |

Developer Twin API logic is implemented in:

```text
backend/app/routes/twin.py
```

## Knowledge Gaps

| Method | Path                         | Description             |
| ------ | ---------------------------- | ----------------------- |
| GET    | `/api/gaps`                  | List knowledge gaps     |
| POST   | `/api/gaps/{gap_id}/resolve` | Resolve a knowledge gap |

## Notifications

| Method | Path                 | Description            |
| ------ | -------------------- | ---------------------- |
| GET    | `/api/notifications` | Retrieve notifications |
| POST   | `/api/notifications` | Create a notification  |

## Modules

| Method | Path                         | Description              |
| ------ | ---------------------------- | ------------------------ |
| POST   | `/modules/quiz/generate`     | Generate a module quiz   |
| POST   | `/modules/quiz/check`        | Check quiz answers       |
| GET    | `/modules/progress`          | Retrieve module progress |
| POST   | `/modules/progress/complete` | Mark a module complete   |

## Analytics

| Method | Path         | Description             |
| ------ | ------------ | ----------------------- |
| GET    | `/analytics` | Retrieve analytics data |

---

# 6. Knowledge Engine API

The Knowledge Engine runs on:

```text
http://127.0.0.1:8001
```

| Method | Path                               | Purpose                             |
| ------ | ---------------------------------- | ----------------------------------- |
| GET    | `/health`                          | Health check                        |
| POST   | `/search`                          | Semantic knowledge search           |
| POST   | `/ingest`                          | Document ingestion                  |
| POST   | `/ingest/repository`               | Repository ingestion                |
| POST   | `/learning-path`                   | Generate personalized learning path |
| GET    | `/gaps`                            | Retrieve knowledge gaps             |
| POST   | `/gaps/{gap_id}/resolve`           | Resolve a knowledge gap             |
| POST   | `/developer-twin`                  | Create or update Developer Twin     |
| GET    | `/developer-twin/{developer_id}`   | Retrieve Developer Twin             |
| POST   | `/developer-twin/apply-evaluation` | Apply assessment evaluation         |
| POST   | `/assessment/generate`             | Generate assessment                 |
| POST   | `/modules/quiz/generate`           | Generate module quiz                |
| POST   | `/modules/quiz/check`              | Check quiz answers                  |
| GET    | `/modules/progress`                | Retrieve module progress            |

The Knowledge Engine also supports developer profile / resume ingestion and skill extraction through:

```text
knowledge-engine/app/ingest_api.py
```

---

# 7. AI Integration API

The AI Integration service runs on:

```text
http://127.0.0.1:8002
```

| Method | Path                   | Purpose                             |
| ------ | ---------------------- | ----------------------------------- |
| POST   | `/generate-answer`     | Generate a grounded Bob answer      |
| POST   | `/evaluate-assessment` | Evaluate developer assessment       |
| POST   | `/generate-curriculum` | Generate curriculum / learning path |

Curriculum generation is implemented in:

```text
ai-integration/app/services/curriculum_service.py
```

---

# 8. Repository Parser API

The Repository Parser runs on:

```text
http://127.0.0.1:8003
```

| Method | Path                       | Purpose                       |
| ------ | -------------------------- | ----------------------------- |
| GET    | `/`                        | Service status                |
| POST   | `/repositories/analyse`    | Analyze a repository          |
| GET    | `/artifacts/{artifact_id}` | Retrieve a generated artifact |

---

# 9. MongoDB Collections

Database:

```text
devora
```

| Collection         | Owner Service    | Purpose                                        |
| ------------------ | ---------------- | ---------------------------------------------- |
| `knowledge_chunks` | Knowledge Engine | Embedded knowledge chunks for semantic search  |
| `raw_documents`    | Knowledge Engine | Original ingested source documents             |
| `projects_meta`    | Knowledge Engine | Project and repository metadata                |
| `knowledge_gaps`   | Knowledge Engine | Detected knowledge gaps                        |
| `developer_twins`  | Knowledge Engine | Developer skill profiles                       |
| `module_progress`  | Knowledge Engine | Learning progress                              |
| `assessments`      | Backend          | Assessment questions, answers, and evaluations |
| `projects`         | Backend          | Project metadata                               |
| `notifications`    | Backend          | Notification feed                              |
| `users`            | Backend          | User accounts                                  |
| `teams`            | Backend          | Team information                               |

---

# 10. MongoDB Atlas Vector Search

The `knowledge_chunks` collection requires an Atlas Vector Search index.

```text
Collection: knowledge_chunks
Index: vector_index
Field: embedding
Dimensions: 384
Similarity: cosine
```

Supported filter fields:

```text
status
project_id
scope
```

Embeddings are generated using:

```text
all-MiniLM-L6-v2
```

---

# 11. Developer Twin

## 11.1 Overview

The **Developer Twin** is DEVORA's representation of a developer's current technical knowledge and learning state.

It can be initialized using the developer's existing skill set / resume and subsequently updated using additional evidence such as assessments, repository intelligence, knowledge gaps, and learning progress.

---

## 11.2 Initial Skill-Set / Resume Upload

DEVORA supports **initial Developer Twin initialization from an uploaded skill set or resume**.

The flow is:

```text
Developer
    │
    ▼
Upload Skill Set / Resume
    │
    ▼
Frontend
    │
    ▼
Backend Twin API
    │
    ▼
Knowledge Engine
    │
    ├── Ingest profile
    ├── Extract skills
    └── Build initial skill profile
    │
    ▼
Developer Twin
    │
    ▼
Personalized Learning Path
```

Relevant implementation files:

```text
backend/app/routes/twin.py
backend/app/services/knowledge_engine.py
knowledge-engine/app/ingest_api.py
knowledge-engine/app/generate_learning_path.py
frontend/client/src/lib/devoraApi.ts
frontend/client/src/pages/Home.tsx
```

---

## 11.3 Developer Twin Data Sources

The Developer Twin can progressively incorporate multiple sources of developer intelligence:

```text
Initial Skill Set / Resume
            │
            ▼
      Initial Skill Profile
            │
            ▼
       Developer Twin
            │
     ┌──────┼──────────┐
     ▼      ▼          ▼
Assessment  Repository  Learning
Results     Intelligence Progress
     │      │          │
     └──────┼──────────┘
            ▼
      Updated Twin
```

This allows DEVORA to start from the developer's existing knowledge rather than treating every developer as a beginner.

---

# 12. Personalized Learning Path

DEVORA's learning path combines multiple sources of developer and project intelligence.

```text
Repository Intelligence
        +
Initial Developer Skill Profile
        +
Developer Twin
        +
Project Knowledge
        +
Knowledge Gaps
        │
        ▼
Curriculum Generation
        │
        ▼
Personalized Learning Path
```

The Knowledge Engine prepares grounded developer and project context.

The AI Integration service uses IBM Bob to generate structured curriculum information.

Relevant implementation:

```text
knowledge-engine/app/generate_learning_path.py
ai-integration/app/services/curriculum_service.py
```

---

# 13. Repository Onboarding Flow

```text
Developer submits GitHub URL
          │
          ▼
POST /api/upload/repository
          │
          ▼
Backend :8000
          │
          ▼
Repository Parser :8003
          │
          ├── File tree
          ├── Languages
          ├── Dependencies
          ├── Modules
          ├── Symbols
          └── Entry points
          │
          ▼
Repository Intelligence
          │
          ▼
Knowledge Engine :8001
          │
          ├── Extract source documents
          ├── Chunk documents
          ├── Generate embeddings
          └── Store in MongoDB Atlas
          │
          ▼
Learning Path Generation
          │
          ▼
AI Integration :8002
          │
          ▼
IBM Bob
          │
          ▼
Structured Curriculum
          │
          ▼
Personalized Learning Path
```

---

# 14. Developer Twin Flow

The current Developer Twin lifecycle is:

```text
Skill Set / Resume
        │
        ▼
Profile Ingestion
        │
        ▼
Initial Skill Profile
        │
        ▼
Developer Twin
        │
        ▼
Repository Intelligence
        │
        ▼
Personalized Learning Path
        │
        ▼
Developer Assessment
        │
        ▼
IBM Bob Evaluation
        │
        ▼
Twin Skill Updates
        │
        ▼
Knowledge Gaps
        │
        ▼
Learning Progress
        │
        ▼
Continuous Personalization
```

---

# 15. Ask Bob Flow

```text
Developer asks question
        │
        ▼
POST /api/ask-bob
        │
        ▼
Backend :8000
        │
        ▼
Knowledge Engine :8001
        │
        ├── Embed query
        ├── Vector search
        └── Retrieve relevant chunks
        │
        ▼
AI Integration :8002
        │
        ▼
IBM Bob
        │
        ▼
Grounded Answer
        │
        ▼
Frontend Bob Assistant
```

Bob receives retrieved DEVORA context and is instructed to answer using the provided knowledge.

---

# 16. Assessment Flow

```text
POST /api/assessments
        │
        ▼
Generate assessment
        │
        ▼
Developer answers questions
        │
        ▼
POST /api/assessments/{id}/submit
        │
        ▼
Knowledge Engine
        │
        └── Retrieve relevant context
        │
        ▼
AI Integration
        │
        ▼
IBM Bob
        │
        ├── Evaluate answers
        ├── Score responses
        └── Identify weak areas
        │
        ▼
Assessment saved
        │
        ▼
Developer Twin updated
        │
        ▼
Knowledge gaps / next focus
```

---

# 17. Module Quiz Flow

Each learning module can include a checkpoint quiz.

```text
Learning Module
      │
      ▼
Quiz Generation
      │
      ▼
5 Questions
      │
      ▼
Developer Answers
      │
      ▼
Answer Evaluation
      │
      ▼
Module Progress Updated
```

Implementation:

```text
knowledge-engine/app/module_quiz.py
```

---

# 18. Environment Variables

All services read configuration from the root `.env` file.

```bash
# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=devora
MONGODB_COLLECTION=knowledge_chunks

# Internal service URLs
KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001
AI_INTEGRATION_URL=http://127.0.0.1:8002
REPOSITORY_PARSER_URL=http://127.0.0.1:8003
DEVORA_AI_INTEGRATION_URL=http://127.0.0.1:8002
DEVORA_BACKEND_URL=http://127.0.0.1:8000

# IBM Bob
BOB_API_KEY=<your-key>
DEVORA_BOB_MODE=mock

# Frontend
VITE_DEVORA_API_URL=http://127.0.0.1:8000/api
```

For live IBM Bob:

```bash
DEVORA_BOB_MODE=live
```

The frontend also requires:

```text
frontend/.env
```

with:

```bash
VITE_DEVORA_API_URL=http://127.0.0.1:8000/api
```

> Never commit `.env` or API keys to the repository. Commit `.env.example` instead.

---

# 19. Installation and Setup

## Prerequisites

* Python 3.10+
* Node.js 18+
* pnpm
* Git
* MongoDB Atlas account
* Optional: IBM Bob CLI and `BOB_API_KEY`

Install pnpm:

```bash
npm install -g pnpm
```

---

## Step 1 — Clone and Configure

```bash
git clone https://github.com/<org>/devora.git
cd devora
```

Create the environment file:

```bash
cp .env.example .env
```

Configure at minimum:

```text
MONGODB_URI
MONGODB_DATABASE
```

---

## Step 2 — Repository Parser

```bash
cd repository-parser
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn api:app --reload --port 8003
```

---

## Step 3 — AI Integration

```bash
cd ai-integration
python -m venv .venv
```

Activate the environment and install:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload --port 8002
```

---

## Step 4 — Knowledge Engine

```bash
cd knowledge-engine
python -m venv .venv
```

Activate the environment and install:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload --port 8001
```

On first startup, the `all-MiniLM-L6-v2` embedding model is downloaded locally.

---

## Step 5 — Backend

```bash
cd backend
python -m venv .venv
```

Activate the environment and install:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## Step 6 — Frontend

```bash
cd frontend
cp .env.example .env
pnpm install
pnpm dev
```

Open:

```text
http://localhost:3000
```

---

# 20. Startup Order

Start the services in the following order:

```text
1. Repository Parser     :8003
2. AI Integration        :8002
3. Knowledge Engine      :8001
4. Backend               :8000
5. Frontend              :3000
```

The dependency flow is:

```text
Repository Parser
        │
        ├───────────────┐
        ▼               │
AI Integration          │
        │               │
        ▼               │
Knowledge Engine        │
        │               │
        ▼               ▼
      Backend :8000
           │
           ▼
      Frontend :3000
```

---

# 21. MCP Server

The MCP server is located at:

```text
devora-mcp/server.py
```

It exposes DEVORA functionality to IBM Bob through MCP.

Primary tool:

```text
search_devora_knowledge
```

The MCP server is configured through the Bob MCP configuration and can be started by Bob when properly registered.

---

# 22. Dependencies

## Backend

```text
fastapi
uvicorn
pydantic
pymongo
python-dotenv
requests
python-multipart
```

## Knowledge Engine

```text
pymongo
sentence-transformers
pypdf
python-dotenv
langchain-text-splitters
python-docx
pydantic
python-multipart
fastapi
uvicorn[standard]
```

## AI Integration

```text
fastapi==0.115.12
uvicorn==0.34.3
pydantic==2.11.4
python-dotenv==1.1.0
mcp==1.9.4
httpx==0.28.1
pytest==8.3.5
```

## Repository Parser

```text
GitPython
```

## Frontend

```json
{
  "react": "^19.2.1",
  "react-dom": "^19.2.1",
  "vite": "^7.1.7",
  "typescript": "5.6.3",
  "tailwindcss": "^4.1.14",
  "wouter": "^3.3.5",
  "framer-motion": "^12.23.22",
  "recharts": "^2.15.2",
  "lucide-react": "^0.453.0",
  "sonner": "^2.0.7",
  "axios": "^1.12.0",
  "zod": "^4.1.12",
  "react-hook-form": "^7.64.0"
}
```

> **Frontend package manager: pnpm.** The repository uses `pnpm-lock.yaml`; use `pnpm install` rather than `npm install`.

---

# 23. Current Implementation Status

| Feature                                        | Status               |
| ---------------------------------------------- | -------------------- |
| React / Vite frontend                          | Implemented          |
| FastAPI backend                                | Implemented          |
| Knowledge Engine                               | Implemented          |
| Repository Parser                              | Implemented          |
| IBM Bob integration                            | Implemented          |
| Bob mock fallback                              | Implemented          |
| MongoDB Atlas                                  | Implemented          |
| MongoDB Atlas Vector Search                    | Implemented          |
| Repository ingestion                           | Implemented          |
| Semantic search                                | Implemented          |
| Grounded Bob Q&A                               | Implemented          |
| Personalized learning path                     | Implemented          |
| Assessment generation                          | Implemented          |
| Bob assessment evaluation                      | Implemented          |
| Developer Twin                                 | Implemented          |
| **Initial skill-set / resume upload**          | **Implemented**      |
| **Initial Developer Twin skill profile**       | **Implemented**      |
| **Skill extraction from uploaded profile**     | **Implemented**      |
| Developer Twin assessment updates              | Implemented          |
| Knowledge-gap tracking                         | Implemented          |
| Module quizzes                                 | Implemented          |
| Module progress                                | Implemented          |
| Notifications                                  | Implemented          |
| MCP integration                                | Implemented          |
| Team Knowledge Heatmap                         | Partially integrated |
| Admin-side automatic "Implement Module" action | Future enhancement   |

---

# 24. Known Issues and Limitations

| Issue                                                               | Status             |
| ------------------------------------------------------------------- | ------------------ |
| `ai-integration/requirements.txt` encoding issue                    | Fixed              |
| Frontend API previously pointing to :8001                           | Fixed              |
| MCP backend port mismatch                                           | Fixed              |
| MCP indentation bug                                                 | Fixed              |
| Notifications database function issue                               | Fixed              |
| Backend Bob placeholder                                             | Fixed              |
| Bob unavailable without fallback                                    | Fixed              |
| Empty `.env.example`                                                | Fixed              |
| BobAssistant using mock service                                     | Fixed              |
| Missing frontend `.env.example`                                     | Fixed              |
| Initial Developer Twin skill-set upload                             | Implemented        |
| Developer Twin frontend still contains some mock/demo display logic | Partial            |
| Team Heatmap frontend still contains some mock/demo data            | Partial            |
| Admin-side automatic "Implement Module" functionality               | Future enhancement |

---

# 25. Important Implementation Files

The following files contain the major implementation involved in the current DEVORA workflow:

| File                                                | Responsibility                                                       |
| --------------------------------------------------- | -------------------------------------------------------------------- |
| `README.md`                                         | Project documentation and architecture overview                      |
| `ai-integration/app/services/curriculum_service.py` | Curriculum / learning-path generation                                |
| `backend/app/routes/twin.py`                        | Developer Twin and profile API flow                                  |
| `backend/app/services/knowledge_engine.py`          | Backend ↔ Knowledge Engine integration                               |
| `frontend/client/src/lib/devoraApi.ts`              | Frontend ↔ Backend API functions                                     |
| `frontend/client/src/lib/devoraMockData.ts`         | Developer Twin display/calculation support                           |
| `frontend/client/src/pages/Home.tsx`                | Main UI, resume flow, assessment, completion, notifications, Twin UI |
| `knowledge-engine/app/generate_learning_path.py`    | Grounded personalized learning-path generation                       |
| `knowledge-engine/app/ingest_api.py`                | Developer profile/resume ingestion and skill extraction              |
| `knowledge-engine/app/module_quiz.py`               | Module checkpoint quiz generation/evaluation                         |

---

# 26. Master Technical Context

> **For an AI coding agent or developer continuing DEVORA:**

DEVORA is a **five-service Python + TypeScript monorepo** with an additional MCP server.

The architecture is:

```text
React / Vite Frontend :3000
          │
          ▼
FastAPI Backend :8000
          │
          ├── Knowledge Engine :8001
          ├── AI Integration :8002
          └── Repository Parser :8003
```

The frontend communicates only with the Backend API.

The Backend orchestrates the remaining services.

The Knowledge Engine is the primary intelligence and data layer. It uses:

```text
all-MiniLM-L6-v2
        │
        ▼
384-dimensional embeddings
        │
        ▼
MongoDB Atlas Vector Search
```

DEVORA's knowledge can originate from:

* Project documentation
* Repository source code
* Uploaded project documents
* Developer skill sets / resumes
* Assessment results
* Learning activity

---

## Developer Twin

The Developer Twin represents the developer's current technical knowledge and learning state.

The current initialization flow is:

```text
Skill Set / Resume
        │
        ▼
Profile Ingestion
        │
        ▼
Skill Extraction
        │
        ▼
Initial Skill Profile
        │
        ▼
Developer Twin
```

The Twin can subsequently incorporate:

```text
Repository Intelligence
Assessment Results
Knowledge Gaps
Learning Progress
```

to continuously refine the developer's profile.

---

## Learning Path

The personalized learning path combines:

```text
Developer Skill Profile
+
Developer Twin
+
Repository Intelligence
+
Project Knowledge
+
Knowledge Gaps
        │
        ▼
Curriculum Generation
        │
        ▼
Personalized Learning Path
```

IBM Bob is used through the AI Integration service for:

* Grounded Q&A
* Assessment evaluation
* Curriculum generation

IBM Bob is invoked through:

```text
bob run
```

A deterministic mock mode is available through:

```text
DEVORA_BOB_MODE=mock
```

The primary frontend API layer is:

```text
frontend/client/src/lib/devoraApi.ts
```

The current implementation contains some mock/demo presentation data in selected frontend components, particularly parts of Developer Twin and Team Knowledge Heatmap visualization. The underlying Developer Twin initialization and backend/Knowledge Engine flow are implemented.

---

## Current Developer Twin Lifecycle

```text
                 ┌──────────────────────┐
                 │ Skill Set / Resume   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Profile Ingestion    │
                 │ + Skill Extraction   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Initial Developer    │
                 │ Twin                 │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Repository           │
                 │ Intelligence         │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Personalized         │
                 │ Learning Path        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Developer            │
                 │ Assessment           │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ IBM Bob Evaluation   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Twin Skill Updates   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Knowledge Gaps       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Learning Progress    │
                 └──────────┬───────────┘
                            │
                            └──────────────► Continuous
                                             Personalization
```

---

## System Summary

DEVORA combines **repository intelligence, semantic search, developer profiling, assessment, personalized learning, and IBM Bob** into a unified developer onboarding platform.

The system is designed around a continuous feedback loop:

```text
Understand the Developer
          ↓
Understand the Project
          ↓
Identify Knowledge Gaps
          ↓
Generate Personalized Learning
          ↓
Assess Progress
          ↓
Update Developer Twin
          ↓
Adapt Learning
```

This architecture allows DEVORA to move beyond static onboarding documentation toward a **developer-aware, project-aware, and continuously personalized onboarding experience**.
