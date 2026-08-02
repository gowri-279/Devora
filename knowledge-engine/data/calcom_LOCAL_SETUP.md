# Local Setup

## Prerequisites

- Node.js 18+
- PostgreSQL 13+
- Yarn

## Setup Steps

1. Clone the repository.
2. Install dependencies with `yarn install`.
3. Copy `.env.example` to `.env`.
4. Configure database credentials.
5. Run database migrations.
6. Start the development server.

## Start Commands

```bash
yarn install
yarn prisma migrate dev
yarn dev
```

The application will start in development mode after the database is configured.