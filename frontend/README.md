# MentorSpace Frontend

Frontend for the MentorSpace / Devora AI Developer Onboarding Platform.

## Backend contract used

The frontend calls the existing FastAPI backend without changing its routes:

- POST `/register`
- POST `/login`
- GET `/dashboard`
- GET `/missions`
- POST `/complete-mission`
- GET `/learning-path`
- POST `/generate-learning-path`
- POST `/upload/repository`
- POST `/upload/documents`
- GET `/notifications`
- GET `/analytics`
- POST `/ask-bob`

## Architecture

Browser / React UI -> FastAPI backend -> MongoDB / Repository Parser / Knowledge Engine / IBM Bob.

The frontend never calls MongoDB, Repository Parser, Knowledge Engine or IBM Bob directly.

## Run

1. Install Node.js.
2. Open this folder.
3. Run `npm install`.
4. Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

5. Run `npm run dev`.
6. Open `http://localhost:3000`.

## Important backend response note

The API screenshots specify routes but do not expose every response/request field. The UI therefore reads common fields defensively (for example `access_token`, `token`, `missions`, `modules`, `answer`) and displays the raw analytics response where appropriate.

If your FastAPI Pydantic schemas use different field names, update only `lib/api.ts` and the small field-picking sections in the relevant pages; the route contract itself remains unchanged.
