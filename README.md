# DEVORA — Intelligent AI-Powered Developer Onboarding

> **AI-powered onboarding that understands your project, evaluates your knowledge, and builds a personalized learning path.**

## 🚀 Overview

**DEVORA** is an AI-powered developer onboarding and knowledge-transfer platform designed to help developers become productive faster when joining an unfamiliar software project.

Traditional onboarding often depends on manually written documentation, generic tutorials, and repeated explanations from senior developers. DEVORA instead understands the **actual project repository and documentation** and transforms that knowledge into an interactive, personalized onboarding experience.

A developer can work with a project repository and supporting documents. DEVORA analyzes the project, builds a searchable knowledge base, identifies relevant repository concepts, generates a grounded learning path, answers project-specific questions, evaluates the developer's understanding, and maintains a **Developer Twin** representing their evolving technical skill profile.

---

# ✨ Key Features

## 🧠 Project-Aware Knowledge Engine

DEVORA ingests project knowledge from:

* GitHub repositories
* PDF documents
* DOCX documents
* Markdown and text documents
* Repository source files

The Knowledge Engine processes project content using **SentenceTransformers (`all-MiniLM-L6-v2`)** and stores searchable knowledge representations in **MongoDB Atlas Vector Search**.

This enables semantic retrieval of relevant project-specific context instead of relying only on generic AI knowledge.

---

## 🔍 Repository Intelligence

DEVORA analyzes the actual repository to identify:

* Programming languages
* Technology stack
* Modules
* Dependencies
* Symbols
* Entry points
* Relevant source files
* Project structure

This repository intelligence becomes part of the foundation for generating the developer's learning experience.

---

## 🗺️ Grounded Personalized Learning Paths

DEVORA combines:

**Project understanding + repository intelligence + developer skill signals + retrieved project knowledge**

to generate a structured onboarding path.

The learning path contains concepts such as:

* Learning modules
* Difficulty and learning progression
* Estimated learning time
* Project-specific lessons
* Why a concept matters in the project
* How the project implements the concept
* Repository exploration tasks
* Source-file references
* Key takeaways

The curriculum is designed around the **actual codebase**, rather than treating every document or source file as an independent lesson.

### Learning flow

```text
Project Repository + Documentation
              ↓
       Knowledge Engine
              ↓
      Project Understanding
              ↓
    Developer Skill Signals
              ↓
      Grounded Curriculum
              ↓
       Interactive Learning
```

---

# 🤖 Ask DEVORA

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
IBM Bob
       ↓
Grounded Answer
```

The Knowledge Engine retrieves relevant project context before the AI generates the answer.

This allows DEVORA to provide **project-specific answers grounded in the available repository and documentation context**.

---

# 📄 Resume → Developer Twin

DEVORA can use a developer's resume/profile as an initial source of skill signals.

```text
Developer Resume
       ↓
Knowledge Engine
       ↓
Skill Extraction
       ↓
Initial Developer Twin
       ↓
Admin Team Heatmap
```

The initial profile provides a starting point for domains such as:

* APIs
* Architecture
* Database
* Security

As the developer progresses through onboarding and completes assessments, the Developer Twin can be updated with new evidence.

---

# 🧬 Developer Twin

DEVORA maintains a dynamic technical profile for each developer.

The Developer Twin represents skill signals across relevant technical domains and can identify:

* Strong areas
* Knowledge gaps
* Areas requiring further learning
* Recommended learning focus

The Twin can be updated using multiple sources of evidence, including the developer's initial profile and assessment results.

### Developer Twin lifecycle

```text
Resume / Initial Profile
          ↓
    Initial Skill Signals
          ↓
     Developer Twin
          ↓
     Learning Path
          ↓
      Assessment
          ↓
    Evaluated Evidence
          ↓
    Updated Developer Twin
          ↓
      Admin Heatmap
```

---

# 📝 AI-Powered Assessments

DEVORA evaluates a developer's understanding through a **five-question assessment** covering practical project-related scenarios.

The assessment focuses on reasoning rather than simple recall.

Example areas include:

* Investigating unexpected API behavior
* Safely adding new functionality
* Diagnosing database performance problems
* Handling authorization issues
* Troubleshooting differences between local and deployed environments

The answers are evaluated using project-relevant context.

The resulting evaluation can include:

* Domain scores
* Overall performance
* Evidence-based feedback
* Summary
* Recommended next focus

Assessment results are used to update the Developer Twin.

---

# 📊 Admin Team Heatmap

Administrators can view developer skill signals through a team-level heatmap.

The heatmap provides visibility into:

* Individual developer skill areas
* Team-level skill distribution
* Knowledge gaps
* Changes following assessment

This allows onboarding progress to be viewed at both the **individual** and **team** level.

---

# 🔎 Knowledge Gap Detection

DEVORA tracks knowledge gaps that emerge when project information is missing or when developers require additional project-specific context.

Knowledge gaps can be surfaced to administrators for review.

Administrators can:

1. View open knowledge gaps
2. Review the developer's question/context
3. Upload supporting knowledge when required
4. Mark the gap as resolved

Resolved gaps can generate notifications for the relevant developer.

```text
Developer Question
       ↓
Knowledge Engine
       ↓
Low / Missing Context
       ↓
Knowledge Gap
       ↓
Admin Review
       ↓
Knowledge Added / Gap Resolved
       ↓
Developer Notification
```

---

# 🤖 IBM Bob Integration

IBM Bob provides the AI intelligence used across key DEVORA workflows.

DEVORA integrates IBM Bob through the **Bob Shell CLI** for:

### 1. Developer Q&A

Project context retrieved by the Knowledge Engine is provided to IBM Bob to generate grounded answers.

### 2. Assessment Evaluation

Developer responses are evaluated against relevant project context.

### 3. Curriculum Generation

Repository intelligence, developer skill information, and project knowledge are combined to generate structured learning content.

IBM Bob is invoked through a controlled subprocess:

```text
bob run --format json --mode ask --max-turns 1
```

DEVORA also supports a deterministic mock mode for development when live Bob credentials are unavailable.

See:

```text
docs/IBM_BOB_INTEGRATION.md
```

for the complete integration details.

---

# 🔮 Bob Recommendation — Planned Next Phase

DEVORA's architecture is designed to support continuous personalization through IBM Bob.

A planned next phase will allow Bob to continuously analyze:

* Developer Twin changes
* Assessment evidence
* Learning progress
* Knowledge gaps
* Project requirements

and recommend additional personalized modules when new learning needs are identified.

This extends DEVORA from a one-time onboarding path toward **continuous project-aware developer development**.

---

# 🔌 MCP Integration

DEVORA also exposes project knowledge to IBM Bob through an **MCP server**.

The MCP server is located at:

```text
devora-mcp/server.py
```

It exposes:

```text
search_devora_knowledge
```

and is registered through:

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

for AI-powered generation and evaluation, and:

```text
IBM Bob → DEVORA
```

through MCP for project knowledge retrieval.

---

# 🏗️ System Architecture

DEVORA consists of independently running application services plus an MCP server.

```text
                         Browser / User
                              │
                              │ HTTP :3000
                              ▼
                 ┌─────────────────────────┐
                 │ Frontend                │
                 │ React + Vite + TS       │
                 │ :3000                   │
                 └────────────┬────────────┘
                              │
                              │ REST /api/*
                              ▼
                 ┌─────────────────────────┐
                 │ Backend API             │
                 │ FastAPI + Python        │
                 │ :8000                   │
                 └──────┬──────────┬───────┘
                        │          │
                     :8001       :8003
                        │          │
                        ▼          ▼
                ┌────────────┐ ┌───────────────┐
                │ Knowledge  │ │ Repository    │
                │ Engine     │ │ Parser        │
                │ :8001      │ │ :8003         │
                └─────┬──────┘ └───────────────┘
                      │
                      ▼
                ┌────────────┐
                │ MongoDB    │
                │ Atlas      │
                └────────────┘
                      │
                      │
                ┌─────▼─────┐
                │ IBM Bob   │
                │ CLI / MCP │
                └───────────┘
```

### Services

| Service           |   Port | Responsibility                                                                   |
| ----------------- | -----: | -------------------------------------------------------------------------------- |
| Frontend          | `3000` | Developer and administrator interface                                            |
| Backend API       | `8000` | Main API gateway and orchestration                                               |
| Knowledge Engine  | `8001` | Knowledge ingestion, retrieval, learning paths, gaps, quizzes and Developer Twin |
| Repository Parser | `8003` | Repository analysis and project intelligence                                     |
| DEVORA MCP        |      — | Exposes DEVORA knowledge to IBM Bob                                              |

The frontend communicates with the **Backend API**, which coordinates the project's knowledge and onboarding workflows.

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

## Repository Onboarding

```text
GitHub Repository
       ↓
Backend :8000
       ↓
Repository Parser :8003
       ↓
Repository Metadata + Source
       ↓
Knowledge Engine :8001
       ↓
Chunking + Embeddings
       ↓
MongoDB Atlas
       ↓
Project Knowledge
       ↓
Grounded Learning Path
```

---

## Developer Onboarding

```text
Developer Login
       ↓
Resume / Profile Upload
       ↓
Initial Developer Twin
       ↓
Admin Heatmap
       ↓
Personalized Learning Path
       ↓
Interactive Project Learning
       ↓
Module Completion
       ↓
Five-Question Assessment
       ↓
Assessment Evaluation
       ↓
Developer Twin Update
       ↓
Admin Heatmap Update
```

---

## Ask DEVORA

```text
Question
   ↓
Backend API
   ↓
Knowledge Engine /search
   ↓
Atlas Vector Search
   ↓
Relevant Project Context
   ↓
IBM Bob
   ↓
Grounded Answer
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
Project Context Retrieval
       ↓
IBM Bob Evaluation
       ↓
Scores + Evidence + Feedback
       ↓
Developer Twin Update
       ↓
Admin Heatmap
```

---

## Knowledge Gaps

```text
Developer Interaction
       ↓
Knowledge Retrieval
       ↓
Missing / Low-Confidence Context
       ↓
Knowledge Gap
       ↓
Admin Review
       ↓
Gap Resolution
       ↓
Developer Notification
```

---

# 🔌 Backend API

The main Backend API runs on port `8000`.

| Method | Endpoint                             | Purpose                         |
| ------ | ------------------------------------ | ------------------------------- |
| POST   | `/api/register`                      | User registration               |
| POST   | `/api/login`                         | User login                      |
| GET    | `/api/dashboard`                     | Dashboard data                  |
| POST   | `/api/learning-path`                 | Generate/retrieve learning path |
| POST   | `/api/upload/repository`             | Ingest GitHub repository        |
| POST   | `/api/upload/documents`              | Upload project documents        |
| GET    | `/api/documents`                     | List project documents          |
| GET    | `/api/projects/{id}/repository`      | Get repository information      |
| POST   | `/api/ask-bob`                       | Ask a project-grounded question |
| POST   | `/api/assessments`                   | Create assessment               |
| POST   | `/api/assessments/{id}/submit`       | Submit assessment               |
| GET    | `/api/developer-twin/{developer_id}` | Retrieve Developer Twin         |
| POST   | `/api/developer-twin/from-resume`    | Create initial Twin from resume |
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
* Repository knowledge discovery
* Learning-path generation
* Developer Twin management
* Resume/profile skill extraction
* Knowledge-gap tracking
* Module quizzes
* Assessment support

### Vector Search

DEVORA uses:

```text
all-MiniLM-L6-v2
```

to generate **384-dimensional embeddings**.

Knowledge vectors are stored in:

```text
knowledge_chunks
```

in MongoDB Atlas.

The configured Atlas Vector Search index is:

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

Configure the required environment variables:

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

For development without live IBM Bob credentials:

```env
DEVORA_BOB_MODE=mock
```

> Keep secrets such as MongoDB credentials and Bob API keys out of source control.

---

# ▶️ Running DEVORA

Run the required services in separate terminals.

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

### Terminal 2 — Knowledge Engine

```bash
cd knowledge-engine

python -m venv .venv

# activate the environment

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8001
```

The first startup downloads the `all-MiniLM-L6-v2` embedding model.

### Terminal 3 — Backend

```bash
cd backend

python -m venv .venv

# activate the environment

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

### Terminal 4 — Frontend

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

The MCP server uses the configured transport to expose DEVORA's project knowledge to IBM Bob.

The primary tool is:

```text
search_devora_knowledge
```

which allows IBM Bob to retrieve relevant project knowledge.

---

# 📚 Documentation

Additional technical documentation is available in:

### `docs/TECHNICAL_SETUP.md`

Contains:

* Architecture
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

### Traditional Developer Onboarding

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

### DEVORA

```text
Project Repository + Documentation
              ↓
      Project Understanding
              ↓
       Developer Profile
              ↓
    Personalized Learning Path
              ↓
     Project-Grounded AI
              ↓
       Continuous Learning
              ↓
          Assessment
              ↓
       Developer Twin
              ↓
      Team Skill Visibility
              ↓
      Knowledge Gap Detection
```

DEVORA creates an intelligent layer around the **project itself**, allowing onboarding to adapt to both the **codebase** and the **developer**.

The goal is not simply to provide documentation.

The goal is to help answer:

> **“What does this developer need to understand about this project, and what should they learn next?”**

---

# 👥 Team

## CtrlAltElite

**DEVORA — Intelligent AI-Powered Developer Onboarding**

Built with:

**IBM Bob · MCP · FastAPI · React · MongoDB Atlas Vector Search · SentenceTransformers · Repository Intelligence**

---
