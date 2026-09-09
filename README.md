# DEVORA — Intelligent AI-Powered Developer Onboarding

> **AI-powered onboarding that understands your project, evaluates your knowledge, and builds a personalized learning path.**

DEVORA is an AI-powered developer onboarding platform that understands a software project's repository and documentation, builds searchable project knowledge, generates a repository-aware learning path, answers project-specific questions with grounded context, evaluates developer knowledge, and maintains a Developer Twin.

Built by **CtrlAltElite** for the IBM hackathon.

---

# 🚀 Overview

Traditional developer onboarding depends heavily on manually written documentation, generic tutorials, and repeated explanations from senior developers.

DEVORA takes a different approach:

```text
GitHub Repository + Project Documentation
                    ↓
          Repository Understanding
                    ↓
             Project Knowledge
                    ↓
        Developer Assessment
                    ↓
       Personalized Learning Path
                    ↓
       Project-Grounded AI Assistant
                    ↓
        Continuous Evaluation
                    ↓
          Knowledge Gap Detection
                    ↓
             Developer Twin
```

DEVORA understands the **actual project**, rather than relying only on generic programming knowledge.

A developer can work through a repository-specific learning path, ask questions about the project, complete module checkpoints, receive grounded answers, and have their technical profile updated from assessment results.

---

# ✨ Key Features

## 🧠 Project-Aware Knowledge Engine

DEVORA can ingest:

* GitHub repositories
* PDF documents
* DOCX documents
* Markdown files
* Source-code files
* Project configuration files

The Knowledge Engine:

1. Loads project content.
2. Preserves raw project documents.
3. Splits content into searchable chunks.
4. Generates embeddings.
5. Stores searchable project knowledge.
6. Performs semantic retrieval.
7. Tracks knowledge gaps.
8. Provides project evidence for AI generation.

Embeddings use:

```text
all-MiniLM-L6-v2
```

which produces 384-dimensional vectors.

Vector search is backed by **MongoDB Atlas Vector Search**.

---

# 🗺️ Repository-Aware Learning Paths

DEVORA analyzes repository intelligence such as:

* Programming languages
* Repository modules
* Dependencies
* Symbols
* Entry points
* Technology stack
* Repository structure
* Relevant source files

The repository information is combined with project knowledge and, where available, Developer Twin information.

The AI integration then generates a structured curriculum containing:

* Learning modules
* Difficulty levels
* Estimated learning time
* Lessons
* Concepts
* Why concepts matter
* Project-specific explanations
* Repository exploration guidance
* Source-file references
* Grounded evidence

The learning path is **generated from the connected repository**, rather than being a fixed hardcoded curriculum.

For example, the verified `fastapi-101` integration generated a dynamic six-module curriculum covering areas such as:

* Database Layer, SQLAlchemy, Models & Migrations
* Service Layer & Domain Exceptions
* JWT Authentication & Security
* Middleware and cross-cutting concerns
* Routers and API surface
* Additional repository-specific material

---

# 🤖 Ask DEVORA

Developers can ask questions about the connected project through the DEVORA assistant.

The verified application flow is:

```text
Developer Question
        ↓
Frontend
        ↓
Backend API :8000
        ↓
Knowledge Engine :8001
        ↓
Semantic Project Search
        ↓
Relevant Project Context
        ↓
AI Integration :8002
        ↓
IBM Bob
        ↓
Grounded Answer
        ↓
Frontend
```

The Knowledge Engine retrieves project-specific evidence before the AI generates the response.

Responses can include:

* Answer
* Confidence
* Relevant source file
* Relevant section
* Retrieved project context

This allows DEVORA to answer questions using the **actual connected codebase and documentation**.

---

# 📊 Developer Twin

DEVORA maintains a technical profile for each developer.

Assessment results can update the Developer Twin across relevant technical domains.

The Developer Twin helps identify:

* Strong areas
* Weak areas
* Knowledge gaps
* Recommended learning focus

The resulting profile can influence future personalized onboarding.

---

# 📝 AI-Powered Assessments

DEVORA provides a five-question developer assessment.

The assessment pipeline is:

```text
Assessment
    ↓
Five Questions
    ↓
Developer Answers
    ↓
Project Context
    ↓
IBM Bob Evaluation
    ↓
Domain Scores
    ↓
Overall Score
    ↓
Evidence-Based Feedback
    ↓
Developer Twin Update
```

The evaluation produces structured information such as:

* Domain scores
* Overall score
* Evidence-based feedback
* Summary
* Recommended next focus

Assessment information is persisted and used to update the Developer Twin.

---

# 🧩 Module Checkpoints

Learning modules can include deterministic formative quizzes.

The module quiz system:

* Generates module-specific multiple-choice questions.
* Uses repository/module data.
* Uses real module information for distractors.
* Does not require an LLM for quiz generation.
* Requires all questions to be answered correctly to pass.
* Records module progress.
* Unlocks the next learning step after successful completion.

This keeps the learning checkpoint deterministic while IBM Bob remains responsible for AI-powered explanation, assessment evaluation, and curriculum generation.

---

# 🔍 Knowledge Gap Detection

DEVORA tracks knowledge gaps discovered during project interaction and developer evaluation.

Knowledge gaps can be surfaced to administrators so the team can identify areas where developers repeatedly need assistance.

This enables team-level onboarding insights instead of only individual-level learning recommendations.

---

# 🤖 IBM Bob Integration

IBM Bob is the AI intelligence layer used by DEVORA.

DEVORA integrates IBM Bob for three major workflows:

### 1. Project Q&A

Retrieved project context is supplied to the AI integration layer so IBM Bob can generate grounded project-specific answers.

### 2. Assessment Evaluation

IBM Bob evaluates developer answers against project-specific evidence and produces structured assessment results.

### 3. Curriculum Generation

IBM Bob transforms repository intelligence, project evidence, and developer information into a structured learning curriculum.

The AI integration supports two modes:

```text
live
```

for real IBM Bob execution, and:

```text
mock
```

for deterministic development/testing without consuming live Bob usage.

The live integration is controlled through:

```env
DEVORA_BOB_MODE=live
```

Development/testing can use:

```env
DEVORA_BOB_MODE=mock
```

Detailed IBM Bob implementation information belongs in:

```text
docs/IBM_BOB_INTEGRATION.md
```

---

# 🔌 MCP Integration

DEVORA also includes an MCP integration intended to expose project knowledge to IBM Bob.

The architectural role of MCP is:

```text
IBM Bob
   ↓
DEVORA MCP
   ↓
DEVORA Backend
   ↓
Knowledge Engine
```

The MCP layer acts as a bridge rather than replacing the Backend or Knowledge Engine.

Where MCP is used, it allows IBM Bob to access DEVORA project knowledge through a dedicated knowledge-search capability.

The MCP implementation is located under:

```text
devora-mcp/
```

and should be configured according to the project's MCP configuration and IBM Bob environment.

---

# 🏗️ System Architecture

DEVORA consists of five primary application services:

```text
                         Browser
                            │
                            │ :3000
                            ▼
                 ┌─────────────────────────┐
                 │ Frontend                 │
                 │ React + Vite + TypeScript│
                 │ :3000                    │
                 └────────────┬────────────┘
                              │
                              │ /api/*
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
               MongoDB Atlas   IBM Bob
```

## Services

| Service           |   Port | Responsibility                                                                       |
| ----------------- | -----: | ------------------------------------------------------------------------------------ |
| Frontend          | `3000` | Developer and administrator interface                                                |
| Backend           | `8000` | Main API gateway and orchestration                                                   |
| Knowledge Engine  | `8001` | Ingestion, retrieval, learning paths, assessments, Developer Twin and knowledge gaps |
| AI Integration    | `8002` | IBM Bob integration and AI generation/evaluation                                     |
| Repository Parser | `8003` | GitHub repository analysis and source-artifact generation                            |
| DEVORA MCP        |      — | MCP bridge for exposing DEVORA knowledge to IBM Bob                                  |

The frontend communicates with the Backend API.

The Backend orchestrates communication with the Repository Parser, Knowledge Engine, and AI Integration services.

---

# 🔄 End-to-End Workflows

## Repository Upload

The verified repository onboarding flow is:

```text
GitHub URL
    ↓
Backend :8000
    ↓
Repository Parser :8003
    ↓
Repository metadata
+
Source artifact
    ↓
Backend extracts source files
    ↓
Knowledge Engine :8001
    ↓
Ingestion
    ↓
Raw documents
    ↓
Chunking
    ↓
Embeddings
    ↓
MongoDB Atlas
    ↓
Repository-aware learning path
    ↓
AI Integration :8002
    ↓
IBM Bob
    ↓
Generated curriculum
    ↓
Frontend Learning Path
```

The Repository Parser exposes a generated source artifact so that downstream services do not need access to the Parser's local filesystem.

---

# 💬 Ask DEVORA Workflow

```text
Question
   ↓
POST /api/ask-bob
   ↓
Backend :8000
   ↓
Knowledge Engine /search
   ↓
MongoDB Atlas Vector Search
   ↓
Relevant project contexts
   ↓
AI Integration
   ↓
IBM Bob
   ↓
Grounded answer
   ↓
Confidence + source references
   ↓
Frontend
```

---

# 📝 Assessment Workflow

```text
Create Assessment
       ↓
Five Questions
       ↓
Developer Answers
       ↓
Backend
       ↓
Knowledge Engine / Project Context
       ↓
AI Integration
       ↓
IBM Bob
       ↓
Evaluation
       ↓
Scores + Feedback
       ↓
Developer Twin
       ↓
MongoDB
```

---

# 🧠 Learning Path Workflow

```text
Repository Metadata
       +
Project Knowledge
       +
Developer Information
       ↓
Knowledge Engine
       ↓
AI Integration
       ↓
IBM Bob
       ↓
Repository-Aware Curriculum
       ↓
Normalized Learning Modules
       ↓
Frontend Learning Path
```

---

# 🏆 Developer Learning Flow

```text
Developer
   ↓
Learning Path
   ↓
Study Module
   ↓
Module Quiz
   ↓
Correct Answer
   ↓
Module Progress Recorded
   ↓
Next Module Unlocked
   ↓
Ask Bob for Explanation
   ↓
Project-Grounded Answer
```

---

# 🔌 Backend API

The main Backend API runs on:

```text
http://127.0.0.1:8000
```

Important application endpoints include:

| Method | Endpoint                             | Purpose                                          |
| ------ | ------------------------------------ | ------------------------------------------------ |
| POST   | `/api/register`                      | User registration                                |
| POST   | `/api/login`                         | User login                                       |
| GET    | `/api/dashboard`                     | Dashboard data                                   |
| POST   | `/api/learning-path`                 | Generate/retrieve repository-aware learning path |
| POST   | `/api/upload/repository`             | Analyze and ingest a GitHub repository           |
| POST   | `/api/upload/documents`              | Upload project documents                         |
| GET    | `/api/documents`                     | List project documents                           |
| GET    | `/api/projects/{id}/repository`      | Retrieve repository information                  |
| POST   | `/api/ask-bob`                       | Ask a project-grounded question                  |
| POST   | `/api/assessments`                   | Create assessment                                |
| POST   | `/api/assessments/{id}/submit`       | Submit assessment                                |
| GET    | `/api/developer-twin/{developer_id}` | Retrieve Developer Twin                          |
| GET    | `/api/gaps`                          | Retrieve knowledge gaps                          |
| POST   | `/api/gaps/{gap_id}/resolve`         | Resolve knowledge gap                            |
| GET    | `/api/notifications`                 | Retrieve notifications                           |
| POST   | `/api/notifications`                 | Create notification                              |
| POST   | `/modules/quiz/generate`             | Generate module quiz                             |
| POST   | `/modules/quiz/check`                | Evaluate module quiz                             |
| GET    | `/modules/progress`                  | Retrieve module progress                         |

> Endpoint availability can depend on the route registration in the current Backend version. The module quiz routes are intentionally shown without the `/api` prefix because that is how the current route is registered.

---

# 🧠 Knowledge Engine

The Knowledge Engine runs on:

```text
http://127.0.0.1:8001
```

### Responsibilities

* Document ingestion
* Repository ingestion
* Raw-document storage
* Text chunking
* Embedding generation
* Semantic search
* Repository-aware learning-path generation
* Assessment/project evidence
* Developer Twin management
* Knowledge-gap tracking
* Module quizzes
* Module progress

---

# 🔎 Vector Search

DEVORA uses:

```text
all-MiniLM-L6-v2
```

to generate:

```text
384-dimensional embeddings
```

The embeddings are stored in MongoDB Atlas and queried through Atlas Vector Search.

The project uses semantic similarity to retrieve relevant project context before AI generation.

---

# 🗄️ MongoDB Atlas

DEVORA uses MongoDB Atlas for project knowledge and application data.

Knowledge Engine collections include:

```text
knowledge_chunks
raw_documents
projects_meta
knowledge_gaps
developer_twins
module_progress
```

Backend application data also uses MongoDB-backed collections such as:

```text
assessments
projects
notifications
users
teams
```

---

# 🛠️ Technology Stack

| Layer               | Technology                             |
| ------------------- | -------------------------------------- |
| Frontend            | React                                  |
| Frontend Build Tool | Vite                                   |
| Frontend Language   | TypeScript                             |
| Package Manager     | pnpm                                   |
| Styling             | Tailwind CSS                           |
| UI Components       | shadcn/ui / Radix UI                   |
| Routing             | Wouter                                 |
| Animations          | Framer Motion                          |
| Charts              | Recharts                               |
| Backend             | FastAPI                                |
| Server              | Uvicorn                                |
| Backend Language    | Python                                 |
| Database            | MongoDB Atlas                          |
| Vector Search       | MongoDB Atlas Vector Search            |
| Embeddings          | SentenceTransformers                   |
| Embedding Model     | `all-MiniLM-L6-v2`                     |
| Document Parsing    | PyPDF / python-docx                    |
| Repository Analysis | Python repository parser / Git tooling |
| AI Integration      | IBM Bob integration service            |
| AI                  | IBM Bob Shell CLI                      |
| MCP                 | Python MCP SDK                         |

---

# 📁 Project Structure

```text
Devora/
├── frontend/
│   └── client/
│       ├── src/
│       │   ├── components/
│       │   ├── lib/
│       │   │   ├── devoraApi.ts
│       │   │   └── devoraMockData.ts
│       │   ├── pages/
│       │   └── ...
│       ├── package.json
│       └── vite.config.*
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── assessment.py
│   │   │   ├── bob.py
│   │   │   ├── module_quiz.py
│   │   │   └── ...
│   │   ├── services/
│   │   └── database/
│   │       └── mongodb.py
│   └── requirements.txt
│
├── knowledge-engine/
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── embeddings.py
│   │   ├── ingest_core.py
│   │   ├── generate_learning_path.py
│   │   ├── gap_tracker.py
│   │   ├── module_quiz.py
│   │   ├── raw_storage.py
│   │   └── ...
│   └── requirements.txt
│
├── ai-integration/
│   ├── app/
│   │   ├── main.py
│   │   ├── evaluator.py
│   │   └── services/
│   │       ├── ibm_bob_client.py
│   │       └── ...
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
│   └── ...
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

Copy the example environment file:

```bash
cp .env.example .env
```

The services use environment variables for their inter-service URLs and external integrations.

Typical local service configuration is:

```env
KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001
AI_INTEGRATION_URL=http://127.0.0.1:8002
REPOSITORY_PARSER_URL=http://127.0.0.1:8003
DEVORA_BACKEND_URL=http://127.0.0.1:8000
VITE_DEVORA_API_URL=http://127.0.0.1:8000/api
```

MongoDB configuration should point to the project's MongoDB Atlas deployment.

For live IBM Bob:

```env
DEVORA_BOB_MODE=live
```

For deterministic local development/testing:

```env
DEVORA_BOB_MODE=mock
```

Do not commit secrets such as MongoDB credentials or Bob credentials.

---

# ▶️ Running DEVORA

Run each primary service in a separate terminal.

## Terminal 1 — Repository Parser

```bash
cd repository-parser
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload --port 8003
```

Windows activation:

```text
.venv\Scripts\activate
```

---

## Terminal 2 — AI Integration

```bash
cd ai-integration
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For development/testing:

```bash
export DEVORA_BOB_MODE=mock
```

For live IBM Bob:

```bash
export DEVORA_BOB_MODE=live
```

Start the service:

```bash
uvicorn app.main:app --reload --port 8002
```

---

## Terminal 3 — Knowledge Engine

```bash
cd knowledge-engine
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

The first startup may download the SentenceTransformers embedding model.

---

## Terminal 4 — Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Terminal 5 — Frontend

```bash
cd frontend/client
pnpm install
pnpm dev
```

Open:

```text
http://localhost:3000
```

---

# 🔌 MCP

The MCP implementation is located at:

```text
devora-mcp/
```

The MCP server acts as a bridge between IBM Bob and DEVORA's Backend/Knowledge Engine rather than implementing a second independent knowledge system.

Conceptually:

```text
IBM Bob
   ↓
MCP Tool
   ↓
DEVORA MCP Server
   ↓
Backend
   ↓
Knowledge Engine
   ↓
Project Knowledge
```

The exact MCP configuration should be taken from the current IBM Bob project configuration rather than assuming a particular configuration filename.

---

# 📚 Documentation

Additional project documentation is available under:

```text
docs/
```

### `docs/TECHNICAL_SETUP.md`

Contains technical setup and project implementation information.

### `docs/IBM_BOB_INTEGRATION.md`

Contains IBM Bob integration details, including:

* Bob integration architecture
* Bob CLI usage
* AI workflows
* Live/mock configuration
* Assessment evaluation
* Curriculum generation
* MCP-related integration information

---

# 🎯 Demo Flow

The recommended hackathon demonstration is:

## 1. Admin connects a repository

Enter a GitHub repository URL.

```text
Admin
  ↓
Backend
  ↓
Repository Parser
  ↓
Repository metadata + source artifact
```

---

## 2. DEVORA ingests the repository

```text
Source files
     ↓
Knowledge Engine
     ↓
Raw documents
     ↓
Chunking
     ↓
Embeddings
     ↓
MongoDB Atlas
```

---

## 3. DEVORA generates the learning path

```text
Repository intelligence
        +
Project knowledge
        +
Developer information
        ↓
AI Integration
        ↓
IBM Bob
        ↓
Repository-aware curriculum
```

---

## 4. Developer opens Learning Path

The developer sees modules generated from the connected project rather than a fixed generic course.

---

## 5. Developer completes a module checkpoint

```text
Module
  ↓
Quiz
  ↓
All answers correct
  ↓
Module completed
  ↓
Next module unlocked
```

---

## 6. Developer asks Bob

Example:

```text
What does this module do?
```

or:

```text
How do I set this project up?
```

The request is grounded in the project's actual knowledge.

---

## 7. Assessment updates the Developer Twin

```text
Assessment
   ↓
IBM Bob evaluation
   ↓
Scores
   ↓
Developer Twin
   ↓
Knowledge gaps
```

---

## 8. Administrator views team knowledge

The administrator can inspect team-level knowledge information and identify areas requiring additional attention.

---

# 🏆 Why DEVORA?

Traditional onboarding:

```text
Read Documentation
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
Repository + Documentation
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
          ↓
     Developer Twin
```

DEVORA creates an intelligent onboarding layer around the **actual software project**, allowing learning to adapt to both the codebase and the developer.

---

# 👥 Team

## CtrlAltElite

**DEVORA — Intelligent AI-Powered Developer Onboarding**

Built with:

* IBM Bob
* MCP
* FastAPI
* React
* Vite
* MongoDB Atlas
* MongoDB Atlas Vector Search
* SentenceTransformers
* Repository intelligence

---
