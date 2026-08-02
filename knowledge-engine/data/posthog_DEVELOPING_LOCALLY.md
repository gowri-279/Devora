# Developing Locally

## Requirements

- Docker
- Node.js
- PostgreSQL

## Start Services

```bash
docker compose up -d
```

## Install Dependencies

```bash
pnpm install
```

## Run the App

```bash
pnpm dev
```

## Common Development Notes

- Ensure PostgreSQL is running.
- Rebuild containers after dependency changes.
- Use environment variables from `.env`.
- Check logs if services fail to start.