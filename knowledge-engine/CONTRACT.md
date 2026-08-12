# DEVORA Knowledge Engine — API Contract

Send this to Backend Lead, Repository Parser Lead, and AI/Bob Integration
Lead today. They can build against this without waiting for the service
to be "done."

Base URL (local dev): `http://localhost:8001`

---

## `GET /health`

Liveness check.

```json
{ "status": "ok" }
```

---

## `GET /stats`

Returns the total number of chunks currently stored in the Knowledge Engine.

```json
{ "total_chunks": 29 }
```

---

## `GET /projects`

Lists all known projects, active and archived, with timestamps.

```json
{
  "projects": [
    {
      "project_id": "refund-service",
      "status": "active",
      "created_at": "...",
      "archived_at": null
    }
  ]
}
```

---

## `GET /projects/active`

Currently active project (or `null` if none yet).

```json
{
  "active_project": {
    "project_id": "refund-service",
    "status": "active",
    "created_at": "..."
  }
}
```

---

## `POST /ingest` — **called by Backend Lead** after doc upload / repo preparation

```json
{
  "project_id": "refund-service",
  "file_paths": [
    "/workspace/refund-service/README.md",
    "/workspace/uploads/meeting-minutes.md"
  ],
  "is_new_project": true
}
```

`is_new_project: true` (default) archives whatever project was previously
active before ingesting this one.

Pass `false` if you are only adding more documents to the currently active
project.

```json
{
  "project_id": "refund-service",
  "documents_processed": 2,
  "chunks_created": 14,
  "chunks_inserted": 14
}
```

---

## `POST /search` — **called by AI/Bob Integration Lead** on every developer question

```json
{
  "project_id": "refund-service",
  "query": "How do I run the project locally?"
}
```

```json
{
  "project_id": "refund-service",
  "query": "How do I run the project locally?",
  "results": [
    {
      "source_file": "calcom_LOCAL_SETUP.md",
      "scope": "project",
      "source_type": "project",
      "score": 0.8123,
      "confidence": "high",
      "section_title": "Local Setup",
      "summary": "Local Setup",
      "reference": "calcom_LOCAL_SETUP.md → Local Setup",
      "answer_preview": "First 180 chars of the context...",
      "context": "Full reconstructed context text — build your IBM Bob prompt from this."
    }
  ],
  "knowledge_gap": null
}
```

### Confidence

`confidence` is one of:

- `high`
- `medium`
- `low`

`warning` is present only when confidence is `low`.

### Trust Layer

Frontend can directly display:

- Team / Project badge (`source_type`)
- Section title (`summary`)
- Confidence
- Preview
- Reference

### Knowledge Gap Loop

When the top result is low confidence:

```json
{
  "gap_id": "64679c96f8944508",
  "query": "How does the payment reconciliation worker recover from partial failures?",
  "example_queries": [
    "How does the payment reconciliation worker recover from partial failures?",
    "Explain how reconciliation failures are retried in the payment worker."
  ],
  "project_id": "refund-service",
  "top_score": 0.6496,
  "asked_by_developer_id": null,
  "status": "open",
  "occurrence_count": 3,
  "first_seen_at": "...",
  "last_seen_at": "..."
}
```

Low-confidence questions are automatically:

- logged,
- semantically deduplicated,
- counted,
- and can later be resolved by Admin.

---

## `GET /gaps` — **Admin analytics**

```http
GET /gaps?project_id=refund-service&min_occurrences=3
```

```json
{
  "gaps": [
    {
      "gap_id": "...",
      "query": "...",
      "occurrence_count": 5
    }
  ]
}
```

Omit `project_id` to see gaps across all projects.

---

## `POST /gaps/{gap_id}/resolve`

Call once Admin has updated the relevant documentation and re-ingested it.

```json
{
  "gap_id": "64679c96f8944508",
  "resolved": true
}
```

---

## `POST /learning-path` — **called by Backend Lead** after onboarding is prepared

```json
{
  "project_id": "refund-service",
  "repo_metadata": null
}
```

`repo_metadata` is optional and reserved for future module-aware learning
paths using the Repository Parser’s `modules.json`.

```json
{
  "project_id": "refund-service",
  "learning_path": [
    {
      "step": 1,
      "title": "Team Foundations",
      "description": "Understand collaboration workflow and engineering standards.",
      "sources": ["team_foundations.md"]
    },
    {
      "step": 2,
      "title": "Project Overview",
      "description": "Understand the project purpose, architecture, and key components.",
      "sources": ["calcom_README.md"]
    },
    {
      "step": 3,
      "title": "Local Setup",
      "description": "Set up the development environment and run the project locally.",
      "sources": [
        "calcom_LOCAL_SETUP.md",
        "posthog_DEVELOPING_LOCALLY.md"
      ]
    }
  ]
}
```

### Dynamic behavior

The learning path is generated dynamically from ingested documents:

- setup-related docs are grouped,
- known document types get custom titles/descriptions,
- unknown docs automatically become fallback learning modules.

---

## What Knowledge Engine still needs from other leads

| From | What | Why |
|---|---|---|
| Repository Parser Lead | Final `modules.json` shape | Needed for future module-aware learning paths |
| Backend Lead | Final workspace path flow | Needed for automatic `/ingest` integration |
| AI/Bob Integration Lead | Final prompt/context format | Needed for optimal answer generation |

---

## Current architecture assumption

During development, teammates may run services on different laptops.

For the final integrated demo, Backend and Knowledge Engine are expected to
run on the same machine (or share the same workspace volume), so the backend
can pass absolute file paths to `/ingest`.

---

## Known limitations

- Team-document replace-in-place is implemented (`raw_storage.py` upserts by
  filename for `scope: "team"`) but not yet exposed as a dedicated update
  endpoint.
- Module-aware learning paths are not enabled yet; they will be added after
  the final `modules.json` contract is agreed.
- Similarity thresholds are tuned for the current MiniLM setup and may still
  need small adjustments after full integration testing.