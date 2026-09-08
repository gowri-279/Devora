# IBM Bob Integration in DEVORA

## Overview

DEVORA integrates **IBM Bob** (IBM's AI assistant platform, accessed via the Bob Shell CLI) as the core intelligence layer for three distinct capabilities:

1. **Developer Q&A** — Answering grounded, project-specific questions during onboarding
2. **Assessment Evaluation** — Evaluating open-ended 5-question developer knowledge assessments
3. **Curriculum Generation** — Generating personalized, project-specific learning paths

---

## How IBM Bob Is Invoked

IBM Bob is invoked through the **Bob Shell CLI** (`bob run`) via a Python subprocess call. This is intentional — it gives DEVORA full access to IBM Bob's reasoning capabilities without requiring a custom REST API integration, and keeps the integration portable across environments.

**Service:** `ai-integration/` (FastAPI, port 8002)  
**Client:** [`ai-integration/app/services/ibm_bob_client.py`](ai-integration/app/services/ibm_bob_client.py)

```python
result = subprocess.run(
    [
        "bob",
        "run",
        "--format", "json",
        "--mode", "ask",
        "--max-turns", "1",
        "--disable-tool-groups", "read,edit,execute,mcp,skill,todo,subagent,mode",
        prompt,
    ],
    capture_output=True,
    text=True,
    timeout=180,
    env=env,
)
```

Key flags used:
- `--format json` — structured output for reliable parsing
- `--mode ask` — constrains Bob to answering, no tool use
- `--max-turns 1` — single-turn, deterministic response
- `--disable-tool-groups` — prevents Bob from invoking filesystem, edit, or MCP tools (security + speed)

---

## Use Case 1: Developer Q&A (`/api/ask-bob`)

**Flow:**

```
Developer asks question
     ↓
Backend (/api/ask-bob)
     ↓
Knowledge Engine (/search) → retrieves top-3 context chunks via MongoDB Atlas Vector Search
     ↓
AI Integration (/generate-answer)
     ↓
IBM Bob Shell CLI receives grounded prompt:
  "You are DEVORA. Answer using ONLY the provided project context..."
     ↓
Answer returned to developer with source file + confidence
```

**Prompt structure** ([`ai-integration/app/services/bob_service.py`](ai-integration/app/services/bob_service.py)):
```
You are DEVORA, an AI onboarding assistant for software developers.
Answer the developer's question using ONLY the provided project context.
Do not invent information that is not present in the context.

Project: <project_id>
Developer question: <question>
Retrieved project context:
  Source: <file>  Section: <title>  Context: <text>
  ...
```

**Why this matters:** IBM Bob never answers from generic training data. Every answer is grounded in the actual uploaded project documentation and source code, preventing hallucination.

---

## Use Case 2: Assessment Evaluation (`/evaluate-assessment`)

After a developer completes the **5-question open-ended assessment**, IBM Bob evaluates their answers against retrieved Knowledge Engine context.

**Flow:**

```
Developer submits 5 answers
     ↓
Backend retrieves context per domain (APIs, Architecture, Database, Security)
     ↓
AI Integration (/evaluate-assessment)
     ↓
IBM Bob receives structured prompt with:
  - All 5 questions + developer answers
  - Domain-specific Knowledge Engine context
     ↓
IBM Bob returns JSON:
  {
    "domain_scores": { "APIs": {"score": 78, "confidence": "HIGH", ...}, ... },
    "overall_score": 73,
    "summary": "...",
    "next_focus": "Database"
  }
     ↓
Scores saved to MongoDB
Developer Twin updated with new skill scores
```

**Prompt builder:** [`ai-integration/app/services/assessment_prompt.py`](ai-integration/app/services/assessment_prompt.py)

IBM Bob is instructed to:
- Score each domain 0–100 based on the quality of the developer's reasoning
- Provide human-readable evidence for each score
- Identify cross-domain reasoning patterns
- Not use generic knowledge — only what is grounded in the retrieved context

**Robust JSON parsing:** [`ai-integration/app/services/assessment_evaluator.py`](ai-integration/app/services/assessment_evaluator.py) handles Markdown fences, multi-line JSON, and partial responses gracefully.

---

## Use Case 3: Curriculum Generation (`/generate-curriculum`)

When a repository is uploaded, DEVORA generates a **personalized learning path** using IBM Bob to interpret the repository structure.

**Flow:**

```
Repository ingested → Knowledge Engine builds repository intelligence
     ↓
Knowledge Engine calls AI Integration (/generate-curriculum)
     ↓
IBM Bob receives:
  - Repository summary (languages, modules, dependencies, tech stack)
  - Repository module metadata (files, symbols, entrypoints)
  - Knowledge Engine evidence chunks (ingested documentation)
  - Developer profile (skill scores from Developer Twin)
     ↓
IBM Bob generates structured JSON curriculum:
  {
    "modules": [
      {
        "title": "...", "difficulty": "medium", "estimated_minutes": 20,
        "lessons": [{ "concept": "...", "why_it_matters": "...", "sources": [...] }]
      }
    ]
  }
     ↓
Curriculum stored and served to the developer as their personalized learning path
```

**Prompt:** [`ai-integration/app/services/curriculum_service.py`](ai-integration/app/services/curriculum_service.py)

IBM Bob is instructed to:
- Identify architectural concepts (not just file listings)
- Order modules from foundational to advanced
- Cite exact source files for every lesson
- Not invent frameworks, APIs, or architecture beyond what the evidence shows

---

## MCP Server: DEVORA as an IBM Bob Tool

DEVORA also exposes itself **back to IBM Bob** as an MCP tool via [`devora-mcp/server.py`](devora-mcp/server.py).

```python
@server.tool()
async def search_devora_knowledge(question: str, project_id: str = "devora") -> str:
    """Search Devora's Knowledge Engine for project information."""
    response = await client.post(f"{DEVORA_BACKEND_URL}/ask-bob", ...)
    return formatted_contexts
```

This creates a **bidirectional integration**: IBM Bob calls DEVORA's Knowledge Engine, and DEVORA's AI Integration calls IBM Bob — forming a closed intelligence loop where Bob can retrieve grounded project knowledge as a tool during any of its reasoning tasks.

**Registration:** The MCP server is registered in `.bob/mcp.json` and runs over stdio transport.

---

## Development Mode (No API Key Required)

When `DEVORA_BOB_MODE=mock` (the default) or `BOB_API_KEY` is absent, the `IBMBobClient` returns deterministic mock responses that satisfy all downstream parsers. This allows the complete pipeline — repository upload → ingestion → learning path generation → assessment → Developer Twin update — to run end-to-end without IBM Bob credentials.

Set `DEVORA_BOB_MODE=live` and provide `BOB_API_KEY` to activate real IBM Bob intelligence.

---

## Configuration

| Environment Variable | Purpose | Default |
|---|---|---|
| `BOB_API_KEY` | IBM Bob authentication key | (none) |
| `IBM_BOB_API_KEY` | Backward-compatible alias | Falls back to `BOB_API_KEY` |
| `DEVORA_BOB_MODE` | `mock` or `live` | `mock` |

Set these in the root `.env` file (see `.env.example`).

---

## Files Reference

| File | Role |
|---|---|
| `ai-integration/app/services/ibm_bob_client.py` | Core Bob Shell subprocess client |
| `ai-integration/app/services/bob_service.py` | Q&A prompt builder + response handler |
| `ai-integration/app/services/assessment_evaluator.py` | Assessment evaluation pipeline |
| `ai-integration/app/services/assessment_prompt.py` | Assessment prompt builder |
| `ai-integration/app/services/curriculum_service.py` | Curriculum generation pipeline |
| `ai-integration/app/routes/bob.py` | FastAPI routes exposing all three endpoints |
| `ai-integration/app/config.py` | `BOB_API_KEY`, `DEVORA_BOB_MODE` config |
| `devora-mcp/server.py` | MCP server exposing DEVORA to IBM Bob |
