# DEVORA — Intelligent AI-Powered Developer Onboarding

> **Transforming complex codebases into personalized developer learning experiences.**

DEVORA is an AI-powered developer onboarding platform designed to help developers understand unfamiliar software projects faster and more effectively.

Instead of relying on static documentation and repetitive explanations from senior developers, DEVORA analyzes a project's repository and documentation, builds a searchable project knowledge base, evaluates developer understanding, identifies knowledge gaps, and generates personalized learning experiences.

DEVORA combines **repository intelligence, semantic knowledge retrieval, personalized learning paths, Developer Twins, knowledge-gap analysis, and IBM Bob** into a modular onboarding platform.

---

## 🚀 Problem

Understanding an existing software project can be difficult for new developers. They need to learn the project's architecture, APIs, database, authentication, dependencies, debugging practices, documentation, and development workflow.

Traditional onboarding relies heavily on static documentation and senior developers manually transferring knowledge. This makes onboarding time-consuming, difficult to personalize, and challenging to measure.

## 💡 Solution

DEVORA converts project-specific technical knowledge into an intelligent onboarding experience.

It analyzes repositories and documentation, creates a semantic knowledge base, retrieves relevant project context, evaluates developer understanding, identifies knowledge gaps, and generates personalized learning paths.

The platform also maintains a **Developer Twin** representing the developer's evolving technical knowledge profile.

IBM Bob is integrated into the AI layer for personalized curriculum generation and assessment evaluation.

---

# ✨ Key Features

### 📂 Repository Intelligence

DEVORA analyzes GitHub repositories to identify:

* Programming languages
* Project modules
* Dependencies
* Symbols
* Entry points
* Repository structure

The Repository Parser converts the repository into structured metadata and source artifacts for further processing.

### 🧠 Project Knowledge Engine

Project source code and documentation are processed into searchable knowledge using:

* Document chunking
* `all-MiniLM-L6-v2` embeddings
* MongoDB Atlas
* MongoDB Atlas Vector Search
* Semantic retrieval

This allows DEVORA to retrieve project-specific context for downstream workflows.

### 🎯 Personalized Learning Paths

Learning paths are generated using information about:

* The project
* Repository structure
* Project documentation
* Developer knowledge
* Identified weak areas

This creates a project-specific onboarding experience rather than a generic programming curriculum.

### 👤 Developer Twin

DEVORA maintains a Developer Twin containing normalized skill scores across areas such as:

* Architecture
* Backend/API
* Database
* Authentication
* Debugging

Assessment results can be applied to the Developer Twin to identify areas requiring further learning.

### 📝 Developer Assessment

DEVORA provides a five-question assessment covering:

1. Architecture
2. Core technical understanding
3. Project-specific implementation
4. Debugging and problem solving
5. Self-assessed knowledge gaps

The assessment is grounded in project knowledge and evaluated using IBM Bob.

### 📊 Knowledge Gap Analysis

Low-confidence knowledge searches can be recorded as knowledge gaps.

When multiple developers encounter similar gaps, DEVORA can identify recurring areas where additional onboarding support may be useful.

### 🤖 IBM Bob Integration

IBM Bob is integrated through a dedicated AI Integration service.

IBM Bob is used for:

* Personalized curriculum generation
* Open-ended assessment evaluation
* Domain-level scoring
* Overall assessment evaluation
* Assessment summaries
* Next learning focus

### 🔌 MCP Integration

DEVORA includes a dedicated MCP server, `devora-mcp`, that exposes DEVORA functionality through the Model Context Protocol.

The MCP server communicates with the DEVORA Backend over HTTP.

---

# 🏗️ Architecture

DEVORA consists of five independently running services and an MCP bridge.

```text
                         ┌─────────────────┐
                         │    Developer    │
                         └────────┬────────┘
                                  │
                                  ▼
                     ┌──────────────────────┐
                     │ Frontend             │
                     │ React + Vite         │
                     │ :3000                │
                     └──────────┬───────────┘
                                │ REST
                                ▼
                     ┌──────────────────────┐
                     │ Backend API          │
                     │ FastAPI              │
                     │ :8000                │
                     └─────┬────┬────┬──────┘
                           │    │    │
                ┌──────────┘    │    └─────────────┐
                ▼               ▼                  ▼
       ┌────────────────┐ ┌───────────────┐ ┌─────────────────┐
       │ Knowledge      │ │ AI Integration│ │ Repository      │
       │ Engine :8001   │ │ :8002         │ │ Parser :8003    │
       └───────┬────────┘ └───────┬───────┘ └─────────────────┘
               │                  │
               ▼                  ▼
       ┌────────────────┐  ┌─────────────┐
       │ MongoDB Atlas  │  │ IBM Bob CLI │
       │ Vector Search  │  │             │
       └────────────────┘  └─────────────┘

                    ┌────────────────┐
                    │ devora-mcp     │
                    │ MCP Server     │
                    └───────┬────────┘
                            │ HTTP
                            ▼
                     Backend :8000
```

---

# 🛠️ Technology Stack

| Layer                | Technologies                              |
| -------------------- | ----------------------------------------- |
| Frontend             | React 19, TypeScript, Vite 7              |
| UI                   | TailwindCSS v4, shadcn/ui, Radix UI       |
| Routing              | Wouter                                    |
| Animation            | Framer Motion                             |
| Visualization        | Recharts                                  |
| Backend              | Python, FastAPI, Uvicorn                  |
| Database             | MongoDB Atlas                             |
| Vector Search        | MongoDB Atlas Vector Search               |
| Embeddings           | Sentence Transformers, `all-MiniLM-L6-v2` |
| Document Processing  | PyPDF, python-docx                        |
| Text Splitting       | LangChain Text Splitters                  |
| Repository Analysis  | GitPython                                 |
| AI                   | IBM Bob                                   |
| AI Integration       | IBM Bob CLI                               |
| Protocol Integration | MCP                                       |
| Package Manager      | pnpm                                      |

---

# 📁 Project Structure

```text
DEVORA/
│
├── frontend/
│   ├── client/
│   │   └── src/
│   │       ├── components/
│   │       ├── pages/
│   │       ├── App.tsx
│   │       └── main.tsx
│   └── server/
│
├── backend/
│   └── app/
│       ├── routes/
│       ├── services/
│       └── main.py
│
├── knowledge-engine/
│   └── app/
│       ├── assessment.py
│       ├── developer_twin.py
│       └── main.py
│
├── repository-parser/
│   ├── api.py
│   └── ...
│
├── ai-integration/
│   └── app/
│       ├── services/
│       │   └── ibm_bob_client.py
│       └── main.py
│
├── devora-mcp/
│   ├── server.py
│   └── test_client.py
│
├── IBM_BOB_INTEGRATION.md
├── .env.example
└── README.md
```

---

# 🔄 End-to-End Data Flow

## Repository Ingestion

```text
GitHub Repository
       ↓
Repository Parser
       ↓
Language / Module / Dependency Analysis
       ↓
Repository Metadata
       ↓
Knowledge Engine
       ↓
Document Processing
       ↓
Embeddings
       ↓
MongoDB Atlas
```

## Personalized Onboarding

```text
Project Repository + Documentation
              ↓
       Knowledge Engine
              ↓
      Project Knowledge
              ↓
       Developer Profile
              ↓
     Learning Path Generation
              ↓
            IBM Bob
              ↓
    Personalized Curriculum
```

## Assessment

```text
Developer
    ↓
5-Question Assessment
    ↓
Backend
    ↓
Knowledge Engine
    ↓
Relevant Project Context
    ↓
AI Integration
    ↓
IBM Bob
    ↓
Scores + Summary
    ↓
Developer Twin
    ↓
Next Learning Focus
```

---

# 🔌 Service Ports

| Service           |   Port |
| ----------------- | -----: |
| Frontend          | `3000` |
| Backend API       | `8000` |
| Knowledge Engine  | `8001` |
| AI Integration    | `8002` |
| Repository Parser | `8003` |

---

# ⚙️ Environment Configuration

DEVORA uses environment variables for service URLs, database configuration, and IBM Bob credentials.

Create a root `.env` file.

Example:

```env
MONGODB_URI=<your-mongodb-atlas-uri>

KNOWLEDGE_ENGINE_URL=http://127.0.0.1:8001
AI_INTEGRATION_URL=http://127.0.0.1:8002
REPOSITORY_PARSER_URL=http://127.0.0.1:8003

BOB_API_KEY=<your-bob-api-key>
```

**Do not commit real credentials or API keys to the repository.**

---

# ▶️ Running Locally

DEVORA currently runs its services independently.

### Repository Parser

```bash
cd repository-parser
pip install -r requirements.txt
uvicorn api:app --reload --port 8003
```

### AI Integration

```bash
cd ai-integration
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

### Knowledge Engine

```bash
cd knowledge-engine
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

DEVORA uses `pnpm`.

```bash
cd frontend
pnpm install
pnpm dev
```

The frontend runs on:

```text
http://localhost:3000
```

---

# 🤖 IBM Bob

IBM Bob is integrated into DEVORA through the AI Integration service.

The service communicates with the Bob CLI using:

```text
bob run --format json --mode ask
```

Bob supports two key DEVORA workflows:

### Curriculum Generation

```text
Knowledge Engine
       ↓
AI Integration
       ↓
IBM Bob
       ↓
Personalized Curriculum
```

### Assessment Evaluation

```text
Developer Answers
       ↓
Project Context
       ↓
AI Integration
       ↓
IBM Bob
       ↓
Domain Scores + Summary
       ↓
Developer Twin
```

For detailed integration information, see:

**[IBM_BOB_INTEGRATION.md](IBM_BOB_INTEGRATION.md)**

---

# 🔌 MCP

The `devora-mcp` service provides an MCP interface to DEVORA.

```text
IBM Bob / MCP Client
        ↓
   devora-mcp
        ↓
 DEVORA Backend
        ↓
 DEVORA Services
```

The MCP server uses the MCP SDK and communicates with the backend over HTTP.

---

# 🗄️ MongoDB Collections

The Knowledge Engine uses MongoDB Atlas collections including:

| Collection         | Purpose                       |
| ------------------ | ----------------------------- |
| `knowledge_chunks` | Embedded project knowledge    |
| `raw_documents`    | Original ingested documents   |
| `projects_meta`    | Project registry              |
| `knowledge_gaps`   | Low-confidence knowledge gaps |
| `developer_twins`  | Developer skill profiles      |
| `module_progress`  | Module and quiz progress      |

---

# 🧪 Testing

Testing utilities are included across the project.

The MCP integration includes:

```text
devora-mcp/test_client.py
```

The system also supports testing of API communication, knowledge retrieval, and the assessment workflow.

---

# 🚧 Implementation Status

The core DEVORA service architecture and backend workflows are implemented.

The most complete end-to-end workflow is:

```text
Frontend
   ↓
Backend
   ↓
Knowledge Engine
   ↓
AI Integration
   ↓
IBM Bob
   ↓
Developer Twin
```

Some frontend visualization components currently use demonstration/mock data while their corresponding live backend APIs are being connected.

The underlying backend capabilities for Developer Twin and knowledge-gap functionality are implemented separately from those frontend visualizations.

---

# 👥 Team

### CtrlAltElite

**Project:** DEVORA — Intelligent AI-Powered Developer Onboarding

```
```
