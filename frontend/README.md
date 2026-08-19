# DEVORA Frontend — Knowledge Engine Redesign

A high-fidelity Next.js 15 / React 19 / TypeScript / Tailwind CSS developer onboarding command center.

## Included UX

- DEVORA secure access portal with mock credentials
- Protected `/cockpit` route
- Admin and Developer mode separation
- Command Center dashboard
- Repository Intelligence flow: URL → analyze → ingestion → module metadata → module detail
- Generic Learning Path with module cards and progress
- Module → quiz → Bob feedback → hint → unlock flow
- Project Knowledge / document ingestion status
- Admin-only Knowledge Gap Analytics
- Admin broadcasts and developer notes feed
- Global persistent Bob assistant with stateful glow, confidence UI, retrieved context and knowledge-gap warnings
- Responsive sidebar/navigation and mobile layout
- React Context state with localStorage-backed learning progress/session

## Run locally

```bash
npm install
npm run dev
```

Then open:

`http://localhost:3000`

## Demo credentials

- Admin: `gowri` / `gowri_lead_secure`
- Developer: `ankita` / `dev_ankita_pass`
- Developer: `hemitha` / `dev_hemitha_pass`
- Developer: `repodev` / `dev_repodev_pass`
- Developer: `knowledge_eng` / `dev_knowledge_pass`

Backend/API calls are intentionally mock-ready so the UI can be connected to the finalized DEVORA backend later.
