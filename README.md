# Personal AI Agent

A personal AI agent (single backend, one memory, one identity) accessible from Windows, iPhone (PWA), and eventually Mac. Powered by Claude via the Anthropic API.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design and [`docs/SETUP.md`](docs/SETUP.md) for local development setup.

## Project status

Currently in **Phase 1 — Local development environment**. See the implementation plan in `docs/ARCHITECTURE.md` for the full phase sequence.

## Folder structure

```
backend/          FastAPI backend (api, agent, memory, tools, auth, database, services)
frontend/          Next.js frontend (PWA)
integrations/     External service clients (Anthropic, Gmail, Calendar, web search)
tests/                Automated tests
docs/                Architecture, setup, and security documentation
```

## Security

Never commit a real `.env` file. See [`docs/SECURITY.md`](docs/SECURITY.md).
