# DEVORA — Complete Technical Setup Guide

> This document gives a complete picture of the DEVORA architecture, tech stack, dependencies, and exact commands needed to install and run every service from scratch on any machine.

---

## 1. Project Architecture

DEVORA is composed of **five independently-running services** that communicate over HTTP, plus one MCP server process.

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / User                      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP  port 3000
┌──────────────────────▼──────────────────────────────────┐
│            Frontend  (Vite + React + TypeScript)        │
│                      port 3000                          │
└──────────────────────┬──────────────────────────────────┘
                       │ REST /api/*  port 8000
┌──────────────────────▼──────────────────────────────────┐
│               Backend API  (FastAPI + Python)           │
│                      port 8000                          │
└──────┬───────────────┬──────────────────┬───────────────┘
       │ :8001         │ :8002            │ :8003
┌──────▼──────┐ ┌──────▼──────┐ ┌────────▼────────┐
│  Knowledge  │ │     AI      │ │   Repository    │
│   Engine   │ │ Integration │ │     Parser      │
│   :8001    │ │   :8002     │ │     :8003       │
└──────┬──────┘ └──────┬──────┘ └─────────────────┘
       │               │ subprocess
       ▼               ▼
   MongoDB Atlas    IBM Bob CLI
   (cloud)          (bob run)
```

**Communication pattern:** Frontend → Backend only. Backend proxies to all other services. No cross-service calls except KE → AI Integration (for curriculum generation).

---

## 2. Complete Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | React | 19.x |
| Frontend build tool | Vite | 7.x |
| Frontend language | TypeScript | 5.6.3 |
| Frontend CSS | TailwindCSS | 4.x |
| Frontend UI components | shadcn/ui (Radix UI) | latest |
| Frontend routing | Wouter | 3.3.5 |
| Frontend animations | Framer Motion | 12.x |
| Frontend charts | Recharts | 2.15.x |
| Frontend HTTP | fetch (native) | — |
| Frontend package manager | pnpm | 10.4.1 |
| Backend framework | FastAPI | latest |
| Backend server | Uvicorn | latest |
| Backend language | Python | 3.10+ |
| Knowledge Engine framework | FastAPI | latest |
| Embeddings model | all-MiniLM-L6-v2 (SentenceTransformers) | local |
| Vector store | MongoDB Atlas Vector Search | cloud |
| Database | MongoDB Atlas | cloud |
| MongoDB driver | PyMongo | latest |
| Document parsing | PyPDF, python-docx | latest |
| Text splitting | LangChain text splitters | latest |
| Repository cloning | GitPython | latest |
| AI Integration framework | FastAPI | 0.115.x |
| AI invocation | IBM Bob Shell CLI (`bob run`) | installed |
| MCP server | mcp Python SDK | 1.9.x |

---

## 3. Directory Structure

```
Devora/
├── .env.example              ← Template for all environment variables
├── .env                      ← Your actual secrets (create from .env.example)
├── frontend/                 ← React SPA + Express static server
│   ├── client/src/           ← All React source code
│   │   ├── App.tsx
│   │   ├── pages/Home.tsx    ← All UI views (4400+ lines)
│   │   ├── components/       ← BobAssistant, DeveloperTwin, TeamKnowledgeHeatmap, Map
│   │   ├── lib/devoraApi.ts  ← All backend API calls
│   │   └── lib/devoraMockData.ts ← Mock/demo data
│   ├── server/index.ts       ← Production Express static server
│   ├── vite.config.ts
│   ├── package.json          ← pnpm project
│   └── .env.example          ← VITE_DEVORA_API_URL
├── backend/                  ← Main API gateway (FastAPI)
│   ├── app/
│   │   ├── main.py           ← FastAPI app, all router registrations
│   │   ├── database/mongodb.py ← MongoDB connection
│   │   ├── routes/           ← auth, dashboard, learning, upload, bob, assessment, twin, gaps, etc.
│   │   └── services/         ← knowledge_engine.py, ai_integration.py, project.py, assessment.py
│   └── requirements.txt
├── knowledge-engine/         ← Semantic search + learning path + twin (FastAPI)
│   ├── app/
│   │   ├── main.py           ← FastAPI app + all route definitions
│   │   ├── db.py             ← MongoDB collections
│   │   ├── search.py         ← Atlas Vector Search
│   │   ├── embeddings.py     ← SentenceTransformers (all-MiniLM-L6-v2)
│   │   ├── ingest_core.py    ← Document chunking + embedding + storage
│   │   ├── generate_learning_path.py ← Personalized curriculum builder
│   │   ├── developer_twin.py ← Skill profile storage/update
│   │   ├── assessment.py     ← 5-question assessment generator
│   │   ├── gap_tracker.py    ← Knowledge gap detection
│   │   └── module_quiz.py    ← Per-module checkpoint quizzes
│   └── requirements.txt
├── ai-integration/           ← IBM Bob interface (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py         ← BOB_API_KEY, DEVORA_BOB_MODE
│   │   ├── routes/bob.py     ← /generate-answer, /evaluate-assessment, /generate-curriculum
│   │   └── services/
│   │       ├── ibm_bob_client.py   ← subprocess bob run
│   │       ├── bob_service.py      ← Q&A
│   │       ├── assessment_evaluator.py ← Assessment scoring
│   │       ├── assessment_prompt.py
│   │       └── curriculum_service.py  ← Learning path generation
│   └── requirements.txt
├── repository-parser/        ← GitHub repo analyzer (FastAPI)
│   ├── api.py                ← FastAPI app + /repositories/analyse
│   ├── parser.py             ← Orchestrates all detectors
│   ├── scanner.py            ← File tree scanner
│   ├── language_detector.py
│   ├── module_detector.py
│   ├── dependency_detector.py
│   ├── symbol_detector.py
│   ├── entrypoint_detector.py
│   ├── tech_stack_detector.py
│   ├── github_clone.py       ← GitPython clone
│   ├── zip_handler.py        ← Source artifact ZIP
│   └── requirements.txt
└── devora-mcp/               ← MCP server (exposes DEVORA to IBM Bob)
    ├── server.py             ← search_devora_knowledge tool
    └── test_client.py
```

---

## 4. All Backend API Endpoints

**Backend runs on port 8000. All routes prefixed with `/api`.**

| Method | Path | Description |
|---|---|---|
| POST | `/register` | User registration |
| POST | `/login` | User login |
| GET | `/dashboard` | Dashboard data |
| POST | `/api/learning-path` | Get personalized learning path |
| POST | `/api/upload/repository` | Ingest a GitHub repo (triggers parse → embed → learning path) |
| POST | `/api/upload/documents` | Upload a document to an existing project |
| GET | `/api/documents` | List project documents |
| GET | `/api/projects/{id}/repository` | Get repo URL for a project |
| POST | `/api/ask-bob` | Ask Bob a grounded question |
| POST | `/api/assessments` | Create a new assessment |
| POST | `/api/assessments/{id}/submit` | Submit answers + trigger Bob evaluation |
| GET | `/api/developer-twin/{developer_id}` | Get Developer Twin for a project |
| GET | `/api/gaps` | List knowledge gaps |
| POST | `/api/gaps/{gap_id}/resolve` | Resolve a knowledge gap |
| GET | `/api/notifications` | Get notifications |
| POST | `/api/notifications` | Create a notification |
| POST | `/modules/quiz/generate` | Generate a module checkpoint quiz |
| POST | `/modules/quiz/check` | Submit quiz answers |
| GET | `/modules/progress` | Get module completion status |
| POST | `/modules/progress/complete` | Mark a module complete |
| GET | `/analytics` | Analytics data |

**Knowledge Engine runs on port 8001** (not called directly from frontend):

| Method | Path |
|---|---|
| GET | `/health` |
| POST | `/search` |
| POST | `/ingest` |
| POST | `/learning-path` |
| GET | `/gaps` |
| POST | `/gaps/{gap_id}/resolve` |
| POST | `/developer-twin` |
| GET | `/developer-twin/{developer_id}` |
| POST | `/developer-twin/apply-evaluation` |
| POST | `/assessment/generate` |
| POST | `/modules/quiz/generate` |
| POST | `/modules/quiz/check` |
| GET | `/modules/progress` |
| POST | `/ingest/repository` |

**AI Integration runs on port 8002**:

| Method | Path |
|---|---|
| POST | `/generate-answer` |
| POST | `/evaluate-assessment` |
| POST | `/generate-curriculum` |

**Repository Parser runs on port 8003**:

| Method | Path |
|---|---|
| GET | `/` |
| POST | `/repositories/analyse` |
| GET | `/artifacts/{artifact_id}` |

---

## 5. MongoDB Collections

**Database name:** `devora` (configurable via `MONGODB_DATABASE`)

| Collection | Owner Service | Purpose |
|---|---|---|
| `knowledge_chunks` | Knowledge Engine | Embedded document chunks for vector search |
| `raw_documents` | Knowledge Engine | Original ingested source files |
| `projects_meta` | Knowledge Engine | Project registry (repo metadata) |
| `knowledge_gaps` | Knowledge Engine | Low-confidence query tracking |
| `developer_twins` | Knowledge Engine | Per-developer skill profiles |
| `module_progress` | Knowledge Engine | Module completion state |
| `assessments` | Backend | Assessment documents + answers + evaluation |
| `projects` | Backend | Project metadata (from backend's perspective) |
| `notifications` | Backend | Admin + developer notification feed |
| `users` | Backend | User accounts |
| `teams` | Backend | Team data |

**MongoDB Atlas Vector Search index** must be created manually:
- Collection: `knowledge_chunks`
- Index name: `vector_index`
- Field: `embedding` (type: `knnVector`, dimensions: 384, similarity: `cosine`)
- Filter fields: `status`, `project_id`, `scope`

---

## 6. Environment Variables

All variables live in the **root `.env` file**. Copy `.env.example` to `.env` and fill in:

```bash
# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=devora
MONGODB_COLLECTION=knowledge_chunks

# Service URLs (defaults work for local)
KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001
AI_INTEGRATION_URL=http://127.0.0.1:8002
REPOSITORY_PARSER_URL=http://127.0.0.1:8003
DEVORA_AI_INTEGRATION_URL=http://127.0.0.1:8002
DEVORA_BACKEND_URL=http://127.0.0.1:8000

# IBM Bob
BOB_API_KEY=<your key>
DEVORA_BOB_MODE=mock   # change to "live" for real Bob

# Frontend
VITE_DEVORA_API_URL=http://127.0.0.1:8000/api
```

The frontend also needs `frontend/.env` (copy from `frontend/.env.example`):
```
VITE_DEVORA_API_URL=http://127.0.0.1:8000/api
```

---

## 7. Installation & Run Commands

### Prerequisites

- Python 3.10+
- Node.js 18+
- pnpm (`npm install -g pnpm`)
- Git
- (Optional) `bob` CLI on PATH + `BOB_API_KEY` for live IBM Bob

### Step 1 — Clone and configure

```bash
git clone https://github.com/<org>/devora.git
cd devora
cp .env.example .env
# Edit .env — add MONGODB_URI at minimum
```

### Step 2 — Repository Parser (Terminal 1)

```bash
cd repository-parser
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload --port 8003
```

### Step 3 — AI Integration (Terminal 2)

```bash
cd ai-integration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

### Step 4 — Knowledge Engine (Terminal 3)

```bash
cd knowledge-engine
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

> First startup downloads the `all-MiniLM-L6-v2` model (~90 MB). This is a one-time download.

### Step 5 — Backend (Terminal 4)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 6 — Frontend (Terminal 5)

```bash
cd frontend
cp .env.example .env          # sets VITE_DEVORA_API_URL
pnpm install
pnpm dev
```

Open **http://localhost:3000** in your browser.

### Step 7 — MCP Server (optional, for IBM Bob tool access)

```bash
cd devora-mcp
# No install needed if ai-integration venv is active
# Registered in .bob/mcp.json — Bob starts it automatically
```

---

## 8. Startup Order (important)

Start services in this order to avoid connection errors:
1. Repository Parser (:8003) — no dependencies
2. AI Integration (:8002) — no dependencies
3. Knowledge Engine (:8001) — calls AI Integration
4. Backend (:8000) — calls all three
5. Frontend (:3000) — calls Backend only

---

## 9. End-to-End Data Flow

### Repository Upload Flow
```
User pastes GitHub URL in frontend
  → POST /api/upload/repository (backend :8000)
  → POST /repositories/analyse (repository-parser :8003)
     ← repo metadata JSON + artifact ZIP URL
  → GET /artifacts/{id} — download ZIP
  → extract source files
  → POST /ingest (knowledge-engine :8001)
     → chunk documents → embed (all-MiniLM-L6-v2) → store in MongoDB Atlas
  → POST /learning-path (knowledge-engine :8001)
     → POST /generate-curriculum (ai-integration :8002)
        → IBM Bob CLI generates structured curriculum JSON
     ← personalized learning path
  ← {project_id, learning_path, ingestion_stats}
```

### Ask Bob Flow
```
Developer types question in BobAssistant
  → POST /api/ask-bob (backend :8000)
  → POST /search (knowledge-engine :8001)
     → embed query → Atlas vector search → top-3 chunks
  → POST /generate-answer (ai-integration :8002)
     → IBM Bob CLI: "Answer using ONLY this context..."
     ← grounded answer string
  ← {answer, contexts, confidence}
  → displayed in BobAssistant with source citation
```

### Assessment Flow
```
POST /api/assessments → creates assessment in MongoDB with 5 questions
Developer answers questions in frontend
POST /api/assessments/{id}/submit →
  → search context per domain (knowledge-engine)
  → POST /evaluate-assessment (ai-integration)
     → IBM Bob scores each answer 0-100 with evidence
  → save evaluation to MongoDB
  → POST /developer-twin/apply-evaluation (knowledge-engine)
     → updates skill scores in developer_twins collection
  ← {overall_score, domain_scores, summary, next_focus}
```

---

## 10. Dependencies Summary

### Python (all services share a common pattern)

```
# backend/requirements.txt
fastapi, uvicorn, pydantic, pymongo, python-dotenv, requests, python-multipart

# knowledge-engine/requirements.txt
pymongo, sentence-transformers, pypdf, python-dotenv,
langchain-text-splitters, python-docx, pydantic, python-multipart, fastapi, uvicorn[standard]

# ai-integration/requirements.txt
fastapi==0.115.12, uvicorn==0.34.3, pydantic==2.11.4, python-dotenv==1.1.0,
mcp==1.9.4, httpx==0.28.1, pytest==8.3.5

# repository-parser/requirements.txt
GitPython
```

### Node / Frontend

```json
"react": "^19.2.1", "react-dom": "^19.2.1",
"vite": "^7.1.7", "typescript": "5.6.3",
"tailwindcss": "^4.1.14", "wouter": "^3.3.5",
"framer-motion": "^12.23.22", "recharts": "^2.15.2",
"lucide-react": "^0.453.0", "sonner": "^2.0.7",
"axios": "^1.12.0", "zod": "^4.1.12",
"@radix-ui/*": various, "react-hook-form": "^7.64.0"
```

---

## 11. Known Issues & Current Status

| Issue | Status | Fix Applied |
|---|---|---|
| `ai-integration/requirements.txt` was corrupt (double-byte encoding) | **Fixed** | Rewritten with correct ASCII encoding |
| `devoraApi.ts` pointed to port 8001 instead of 8000 | **Fixed** | Updated default URL |
| `devora-mcp/server.py` pointed to port 8001 (KE) instead of 8000 (backend) | **Fixed** | Updated default |
| `devora-mcp/server.py` had indentation bug causing `return` inside loop | **Fixed** | Corrected indentation |
| `backend/routes/notifications.py` called `get_database()` (undefined) | **Fixed** | Changed to `get_db()` |
| `backend/routes/bob.py` returned placeholder instead of calling IBM Bob | **Fixed** | Wired to AI Integration |
| `ai-integration` had no mock fallback — crashed without Bob CLI | **Fixed** | Added `_mock_response()` gated by `DEVORA_BOB_MODE` |
| `.env.example` was empty | **Fixed** | Fully documented |
| `BobAssistant.tsx` used mock service, never called backend | **Fixed** | Calls `/api/ask-bob` |
| `frontend/.env` missing (no `VITE_DEVORA_API_URL`) | **Fixed** | Added `frontend/.env.example` |
| `DeveloperTwin.tsx` and `TeamKnowledgeHeatmap.tsx` use mock data | Partial — backend data exists, frontend not yet wired | Future work |

---

## 12. MASTER TECHNICAL CONTEXT

> For an AI coding agent continuing this project:

**DEVORA** is a 5-service Python+TypeScript monorepo. Services communicate over HTTP. The frontend (React/Vite, `:3000`) calls only the backend (FastAPI, `:8000`). The backend proxies to: Knowledge Engine (FastAPI, `:8001`), AI Integration (FastAPI, `:8002`), Repository Parser (FastAPI, `:8003`). All Python services load environment variables from the **root `.env` file**.

**The Knowledge Engine** is the data core. It embeds documents with `all-MiniLM-L6-v2` (SentenceTransformers), stores 384-dimensional vectors in MongoDB Atlas (`knowledge_chunks` collection), and retrieves via `$vectorSearch` aggregation with `project_id` and `status != archived` filters. The Atlas index name must be `vector_index`.

**IBM Bob** is invoked via `subprocess.run(["bob", "run", "--format", "json", "--mode", "ask", "--max-turns", "1", ...])` in `ai-integration/app/services/ibm_bob_client.py`. When `DEVORA_BOB_MODE=mock` or no `BOB_API_KEY`, the client returns deterministic JSON mocks that pass all downstream validators.

**The assessment pipeline** is: `POST /api/assessments` (creates with `ASSESSMENT_QUESTIONS`) → `POST /api/assessments/{id}/submit` → KE search for context → AI Integration `/evaluate-assessment` → IBM Bob scores 4 domains → save to `assessments` collection → `developer_twins` updated.

**The learning path pipeline** is: `POST /ingest` (chunk+embed) → `POST /learning-path` → KE builds `repository_intelligence` → calls AI Integration `/generate-curriculum` → IBM Bob generates JSON curriculum → personalized by `developer_twin` weak skills.

**Frontend API layer** is entirely in `frontend/client/src/lib/devoraApi.ts`. All calls hit `VITE_DEVORA_API_URL` (default `http://127.0.0.1:8000/api`). Mock data lives in `devoraMockData.ts` and is still used by `DeveloperTwin.tsx` and `TeamKnowledgeHeatmap.tsx` — these are the two components not yet wired to live backend data.

**MongoDB has two separate connections**: Backend uses `backend/app/database/mongodb.py` (collections: `assessments`, `projects`, `notifications`, `users`, `teams`). Knowledge Engine uses `knowledge-engine/app/db.py` (collections: `knowledge_chunks`, `raw_documents`, `projects_meta`, `knowledge_gaps`, `developer_twins`, `module_progress`). Both read `MONGODB_URI` from the root `.env`.

**Package manager for frontend: pnpm only.** `npm install` will fail due to `pnpm-lock.yaml`.
