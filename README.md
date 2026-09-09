# DEVORA — Intelligent AI-Powered Developer Onboarding

> **AI-powered onboarding that understands your project, evaluates your knowledge, and builds a personalized learning path.**

## 🚀 Overview

**DEVORA** is an AI-powered developer onboarding platform designed to make developers productive faster when joining an unfamiliar software project.

Traditional onboarding depends on manually written documentation, generic tutorials, and repeated explanations from senior developers. DEVORA instead understands the **actual project repository and documentation** and turns that knowledge into an interactive, personalized onboarding experience.

A developer can provide a GitHub repository and project documents. DEVORA analyzes them, builds a searchable project knowledge base, generates a personalized learning path, answers project-specific questions using grounded context, evaluates the developer's understanding, and maintains a **Developer Twin** representing their technical skill profile.

---

## ✨ Key Features

### 🧠 Project-Aware Knowledge Engine

DEVORA ingests:

* GitHub repositories
* PDF documents
* DOCX documents
* Markdown and source files

The Knowledge Engine processes the content using **SentenceTransformers (`all-MiniLM-L6-v2`)**, generating 384-dimensional embeddings that are stored in **MongoDB Atlas Vector Search**.

This enables semantic retrieval of relevant project-specific knowledge.

---

### 🗺️ Personalized Learning Paths

DEVORA analyzes a repository's:

* Programming languages
* Modules
* Dependencies
* Symbols
* Entry points
* Technology stack
* Relevant source files

This repository intelligence is combined with the developer's skill profile and retrieved project knowledge.

**IBM Bob** generates a structured curriculum containing:

* Learning modules
* Difficulty levels
* Estimated learning time
* Lessons
* Concepts
* Why each concept matters
* Source-file references

The resulting learning path is personalized to both the **project and the developer**.

---

### 🤖 Ask DEVORA

Developers can ask questions about their project through the DEVORA AI assistant.

```text
Developer Question
       ↓
Backend API
       ↓
Knowledge Engine
       ↓
MongoDB Atlas Vector Search
       ↓
Relevant Project Context
       ↓
AI Integration
       ↓
IBM Bob
       ↓
Grounded Answer
```

The Knowledge Engine retrieves the most relevant project context before IBM Bob generates the response.

This allows DEVORA to provide **project-specific answers with supporting source context**, rather than relying solely on generic AI knowledge.

---

### 📊 Developer Twin

DEVORA maintains a dynamic technical profile for each developer.

Assessment results are used to build and update the developer's skill profile across relevant technical domains.

The Developer Twin helps identify:

* Strong areas
* Weak areas
* Knowledge gaps
* Recommended learning focus

The profile can then influence future personalized learning paths.

---

### 📝 AI-Powered Assessments

DEVORA evaluates a developer's understanding through a five-question assessment.

The developer's answers are evaluated by IBM Bob using relevant project context retrieved by the Knowledge Engine.

The evaluation produces:

* Domain scores
* Overall score
* Evidence-based feedback
* Summary
* Recommended next focus

The results are stored and used to update the Developer Twin.

---

### 🔍 Knowledge Gap Detection

DEVORA tracks areas where developers demonstrate low confidence or repeatedly require information.

These knowledge gaps can be surfaced to administrators to identify common areas of difficulty across the development team.

---

# 🤖 IBM Bob Integration

IBM Bob is a core intelligence layer within DEVORA.

DEVORA integrates IBM Bob through the **Bob Shell CLI** for three major workflows:

### 1. Developer Q&A

The Knowledge Engine retrieves project-specific context and provides it to IBM Bob, which generates a grounded answer.

### 2. Assessment Evaluation

IBM Bob evaluates developer responses against project-specific context and generates structured scores and feedback.

### 3. Curriculum Generation

IBM Bob converts repository intelligence, retrieved project knowledge, and developer skill information into a structured personalized learning curriculum.

IBM Bob is invoked through a controlled subprocess:

```text
bob run --format json --mode ask --max-turns 1
```

DEVORA also supports a deterministic mock mode for development when live Bob credentials are unavailable.

For the complete IBM Bob implementation, see:

**`docs/IBM_BOB_INTEGRATION.md`**

---

# 🔌 MCP Integration

DEVORA also exposes its project knowledge to IBM Bob through an **MCP server**.

The MCP server is located at:

```text
devora-mcp/server.py
```

It exposes the tool:

```text
search_devora_knowledge
```

The server is registered through:

```text
.bob/mcp.json
```

### MCP Flow

```text
IBM Bob
   ↓
search_devora_knowledge
   ↓
DEVORA MCP Server
   ↓
Backend API
   ↓
Knowledge Engine
   ↓
MongoDB Atlas Vector Search
   ↓
Relevant Project Knowledge
```

This creates a two-way integration:

```text
DEVORA → IBM Bob
```

for AI-powered generation and evaluation, and

```text
IBM Bob → DEVORA
```

through MCP for project knowledge retrieval.

---

# 🏗️ System Architecture

DEVORA consists of **five independently running services**, plus an MCP server process.

```text
                         Browser / User
                              │
                              │ HTTP :3000
                              ▼
                 ┌─────────────────────────┐
                 │ Frontend                 │
                 │ React + Vite + TypeScript│
                 │ :3000                    │
                 └────────────┬────────────┘
                              │
                              │ REST /api/*
                              ▼
                 ┌─────────────────────────┐
                 │ Backend API              │
                 │ FastAPI + Python         │
                 │ :8000                    │
                 └──────┬──────┬──────┬────┘
                        │      │      │
                    :8001   :8002   :8003
                        │      │      │
                        ▼      ▼      ▼
                 ┌────────┐ ┌──────┐ ┌──────────┐
                 │Knowledge│ │ AI   │ │Repository│
                 │ Engine  │ │Integr.│ │ Parser   │
                 │ :8001   │ │:8002 │ │ :8003    │
                 └────┬────┘ └──┬───┘ └──────────┘
                      │          │
                      ▼          ▼
               MongoDB Atlas   IBM Bob CLI
```

### Services

| Service           |   Port | Responsibility                                                |
| ----------------- | -----: | ------------------------------------------------------------- |
| Frontend          | `3000` | Developer and admin interface                                 |
| Backend           | `8000` | Main API gateway and orchestration                            |
| Knowledge Engine  | `8001` | Ingestion, semantic search, learning paths and Developer Twin |
| AI Integration    | `8002` | IBM Bob interface                                             |
| Repository Parser | `8003` | GitHub repository analysis                                    |
| DEVORA MCP        |      — | Exposes DEVORA knowledge to IBM Bob                           |

The frontend communicates only with the Backend API. The Backend acts as the gateway to the other services.

---

# 🛠️ Technology Stack

| Layer               | Technology                  |
| ------------------- | --------------------------- |
| Frontend            | React 19                    |
| Build Tool          | Vite 7                      |
| Language            | TypeScript 5.6              |
| Styling             | TailwindCSS 4               |
| UI Components       | shadcn/ui + Radix UI        |
| Routing             | Wouter                      |
| Animations          | Framer Motion               |
| Charts              | Recharts                    |
| Backend             | FastAPI                     |
| Server              | Uvicorn                     |
| Backend Language    | Python 3.10+                |
| Embeddings          | SentenceTransformers        |
| Embedding Model     | `all-MiniLM-L6-v2`          |
| Vector Search       | MongoDB Atlas Vector Search |
| Database            | MongoDB Atlas               |
| Document Parsing    | PyPDF, python-docx          |
| Text Splitting      | LangChain Text Splitters    |
| Repository Analysis | GitPython                   |
| AI Integration      | FastAPI                     |
| AI                  | IBM Bob Shell CLI           |
| MCP                 | Python MCP SDK              |
| Package Manager     | pnpm                        |

---

# 📁 Project Structure

```text
Devora/
├── frontend/
│   ├── client/src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   └── lib/
│   │       ├── devoraApi.ts
│   │       └── devoraMockData.ts
│   ├── server/
│   ├── vite.config.ts
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── database/
│   └── requirements.txt
│
├── knowledge-engine/
│   ├── app/
│   │   ├── main.py
│   │   ├── search.py
│   │   ├── embeddings.py
│   │   ├── ingest_core.py
│   │   ├── generate_learning_path.py
│   │   ├── developer_twin.py
│   │   ├── assessment.py
│   │   ├── gap_tracker.py
│   │   └── module_quiz.py
│   └── requirements.txt
│
├── ai-integration/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   └── services/
│   │       ├── ibm_bob_client.py
│   │       ├── bob_service.py
│   │       ├── assessment_evaluator.py
│   │       └── curriculum_service.py
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
│   └── zip_handler.py
│
├── devora-mcp/
│   ├── server.py
│   └── test_client.py
│
├── docs/
│   ├── TECHNICAL_SETUP.md
│   └── IBM_BOB_INTEGRATION.md
│
└── .env.example
```

---

# 🔄 End-to-End Workflows

## Repository Upload

```text
GitHub URL
    ↓
Backend :8000
    ↓
Repository Parser :8003
    ↓
Repository metadata + source artifact
    ↓
Knowledge Engine :8001
    ↓
Chunking + Embeddings
    ↓
MongoDB Atlas
    ↓
Learning Path Generation
    ↓
AI Integration :8002
    ↓
IBM Bob
    ↓
Personalized Curriculum
```

---

## Ask DEVORA

```text
Question
   ↓
POST /api/ask-bob
   ↓
Knowledge Engine /search
   ↓
Atlas Vector Search
   ↓
Top relevant chunks
   ↓
AI Integration /generate-answer
   ↓
IBM Bob
   ↓
Grounded answer
   ↓
Frontend
```

---

## Assessment

```text
Create Assessment
       ↓
Five Questions
       ↓
Developer Answers
       ↓
Knowledge Engine
       ↓
Domain-Specific Context
       ↓
AI Integration
       ↓
IBM Bob
       ↓
Evaluation
       ↓
Scores + Feedback
       ↓
MongoDB
       ↓
Developer Twin Update
```

---

# 🔌 Backend API

The main Backend API runs on port `8000`.

| Method | Endpoint                             | Purpose                         |
| ------ | ------------------------------------ | ------------------------------- |
| POST   | `/api/register`                      | User registration               |
| POST   | `/api/login`                         | User login                      |
| GET    | `/api/dashboard`                     | Dashboard data                  |
| POST   | `/api/learning-path`                 | Get personalized learning path  |
| POST   | `/api/upload/repository`             | Ingest GitHub repository        |
| POST   | `/api/upload/documents`              | Upload project documents        |
| GET    | `/api/documents`                     | List project documents          |
| GET    | `/api/projects/{id}/repository`      | Get repository information      |
| POST   | `/api/ask-bob`                       | Ask a project-grounded question |
| POST   | `/api/assessments`                   | Create assessment               |
| POST   | `/api/assessments/{id}/submit`       | Submit assessment               |
| GET    | `/api/developer-twin/{developer_id}` | Retrieve Developer Twin         |
| GET    | `/api/gaps`                          | Retrieve knowledge gaps         |
| POST   | `/api/gaps/{gap_id}/resolve`         | Resolve knowledge gap           |
| GET    | `/api/notifications`                 | Retrieve notifications          |
| POST   | `/api/notifications`                 | Create notification             |
| POST   | `/modules/quiz/generate`             | Generate module quiz            |
| POST   | `/modules/quiz/check`                | Evaluate quiz                   |
| GET    | `/modules/progress`                  | Get module progress             |
| POST   | `/modules/progress/complete`         | Complete module                 |
| GET    | `/analytics`                         | Retrieve analytics              |

---

# 🧠 Knowledge Engine

The Knowledge Engine runs on port `8001`.

### Responsibilities

* Document ingestion
* Repository ingestion
* Text chunking
* Embedding generation
* Semantic search
* Learning-path generation
* Developer Twin management
* Knowledge-gap tracking
* Module quizzes
* Assessment generation

### Vector Search

DEVORA uses:

```text
all-MiniLM-L6-v2
```

to generate **384-dimensional embeddings**.

Vectors are stored in:

```text
knowledge_chunks
```

in MongoDB Atlas.

The Atlas Vector Search index is:

```text
vector_index
```

using cosine similarity.

---

# 🗄️ MongoDB

DEVORA uses **MongoDB Atlas**.

### Knowledge Engine Collections

* `knowledge_chunks`
* `raw_documents`
* `projects_meta`
* `knowledge_gaps`
* `developer_twins`
* `module_progress`

### Backend Collections

* `assessments`
* `projects`
* `notifications`
* `users`
* `teams`

---

# ⚙️ Setup

## Prerequisites

* Python 3.10+
* Node.js 18+
* pnpm
* Git
* MongoDB Atlas
* IBM Bob CLI for live Bob integration

---

## 1. Clone the Repository

```bash
git clone https://github.com/gowri-279/Devora.git
cd Devora
```

---

## 2. Configure Environment Variables

```bash
cp .env.example .env
```

Configure:

```env
MONGODB_URI=<your MongoDB connection string>
MONGODB_DATABASE=devora

KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001
AI_INTEGRATION_URL=http://127.0.0.1:8002
REPOSITORY_PARSER_URL=http://127.0.0.1:8003
DEVORA_BACKEND_URL=http://127.0.0.1:8000

BOB_API_KEY=<your IBM Bob key>
DEVORA_BOB_MODE=live

VITE_DEVORA_API_URL=http://127.0.0.1:8000/api
```

For development without a live IBM Bob credential:

```env
DEVORA_BOB_MODE=mock
```

---

# ▶️ Running DEVORA

Run each service in a separate terminal.

### Terminal 1 — Repository Parser

```bash
cd repository-parser
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn api:app --reload --port 8003
```

### Terminal 2 — AI Integration

```bash
cd ai-integration
python -m venv .venv

# activate the environment
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8002
```

### Terminal 3 — Knowledge Engine

```bash
cd knowledge-engine
python -m venv .venv

# activate the environment
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8001
```

The first startup downloads the `all-MiniLM-L6-v2` embedding model.

### Terminal 4 — Backend

```bash
cd backend
python -m venv .venv

# activate the environment
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

### Terminal 5 — Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Open:

```text
http://localhost:3000
```

---

# 🔌 MCP Setup

The DEVORA MCP server is located at:

```text
devora-mcp/server.py
```

It is registered through:

```text
.bob/mcp.json
```

IBM Bob starts the MCP server through the configured stdio transport.

The MCP server exposes:

```text
search_devora_knowledge
```

which allows IBM Bob to retrieve relevant DEVORA project knowledge.

---

# 📚 Documentation

Additional technical documentation is available in:

### `docs/TECHNICAL_SETUP.md`

Contains:

* Complete architecture
* Technology stack
* Directory structure
* API endpoints
* MongoDB collections
* Environment variables
* Installation instructions
* Startup order
* End-to-end data flows
* Dependencies

### `docs/IBM_BOB_INTEGRATION.md`

Contains:

* IBM Bob architecture
* Bob Shell CLI invocation
* Developer Q&A
* Assessment evaluation
* Curriculum generation
* MCP integration
* Mock/live configuration
* Relevant implementation details

---

# 🎯 The DEVORA Approach

Traditional developer onboarding:

```text
Documentation
     ↓
Explore Repository
     ↓
Ask Senior Developers
     ↓
Figure Out What To Learn
     ↓
Start Contributing
```

DEVORA:

```text
Project Repository + Documentation
              ↓
      Project Understanding
              ↓
       Developer Assessment
              ↓
   Personalized Learning Path
              ↓
     Project-Grounded AI
              ↓
       Continuous Evaluation
              ↓
       Knowledge Gap Detection
```

DEVORA creates an intelligent layer around the **project itself**, allowing onboarding to adapt to both the **codebase** and the **developer**.

---

# 👥 Team

## CtrlAltElite

**DEVORA — Intelligent AI-Powered Developer Onboarding**

Built with **IBM Bob, MCP, FastAPI, React, MongoDB Atlas Vector Search, SentenceTransformers, and repository intelligence.**
