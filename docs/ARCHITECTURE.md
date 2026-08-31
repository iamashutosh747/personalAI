# Architecture

## Vision

One personal AI identity, one memory, one agent, multiple interfaces (Windows, iPhone, Mac). All devices talk to the same centralized backend — no per-device logic or state.

```
Windows / iPhone / Mac (browser or installed PWA)
                │
        Next.js frontend (Vercel)
                │  HTTPS + SSE (streaming)
        FastAPI backend
                │
        Agent Orchestrator (single agent, Python)
                │
        Claude (Anthropic API)
         ├── answers directly
         └── requests a tool call
                │
        Tool Registry (search_web, search_email, get_calendar_events, ...)
                │
        External services (Gmail API [read-only], Calendar API [read-only], Web Search)
                │
        PostgreSQL + pgvector
         ├── conversations / messages
         ├── long-term memory (with embeddings)
         ├── user profile
         ├── tasks
         ├── audit log
         └── encrypted OAuth tokens
```

## Technology stack

| Layer | Choice |
|---|---|
| AI | Anthropic Claude API. Model IDs are **never hard-coded** — set via `CLAUDE_MODEL_MAIN` / `CLAUDE_MODEL_UTILITY` env vars. |
| Embeddings | Voyage AI |
| Backend | Python 3.12 + FastAPI |
| Frontend | Next.js (React, TypeScript), PWA |
| Database | PostgreSQL + `pgvector` (Supabase) |
| Auth | Simple, single-user-appropriate auth for V1; every table scoped by `user_id` for future multi-user support |
| Google integration | Official `google-api-python-client` + OAuth2 — **read-only** for V1 (no send/delete/modify) |
| Web search | Claude's native server-side web search tool |
| Hosting | Vercel (frontend), Fly.io/Railway (backend), Supabase (DB) |

## Agent / tool architecture

Single agent, not multi-agent. Orchestrator loop: call Claude → if it requests a tool, look it up in the tool registry, check its permission level, execute or request confirmation, feed the result back → repeat until Claude returns a final answer. Each tool is a self-contained module with name, description, input/output schema, permission level, error handling, and logging.

### Permission levels

- **READ** — no confirmation required (read calendar, search email, web search, retrieve memory).
- **PREPARE** — agent can draft/prepare but not execute externally (draft email, prepare event).
- **EXECUTE** — requires explicit user confirmation before running (send email, delete, modify calendar/files). **Not implemented for Gmail/Calendar in V1** — those integrations are read-only until the EXECUTE + confirmation flow is built and tested.

## Agent Control Center

A settings surface where the user can see connected services and configure permission level per capability, e.g.:

- Gmail: read / draft / send
- Calendar: read / create / modify
- Files: read / create / modify

Every potentially consequential action is clearly labeled as automatic (READ) or requiring confirmation (EXECUTE). Built out incrementally as each integration is added; V1 starts with visibility into connected services and their (fixed, read-only) permissions.

## Memory architecture

- **Short-term** — current conversation history, compressed/summarized as it grows.
- **Long-term** — `memories` table (`content`, `category`, `importance`, `confidence`, `source`, `embedding`, `created_at`, `expires_at`). Written only when a cheap classification step (utility model) judges something durable.
- **User profile** — stable facts, edited explicitly.
- **Project/context memory** — same `memories` table, tagged by project, retrieved via vector similarity search scoped to the user.

## Audit log (first-class component from V1)

Every tool call, tool result/status, permission check, approval, rejection, and externally visible action is recorded with: timestamp, user, conversation, tool name, input, result status, and duration. Never logs API keys, passwords, OAuth secrets, or full sensitive payloads.

## Authentication / security

- Simple single-user auth for V1 (no full multi-tenant auth provider needed yet), but every row in every table (`conversations`, `messages`, `memories`, `tasks`, `oauth_tokens`, `audit_log`) is scoped by `user_id` from day one.
- OAuth refresh tokens encrypted at rest (Fernet, key from `TOKEN_ENCRYPTION_KEY`).
- Secrets only ever live in backend environment variables, never in frontend code or source control.
- HTTPS in production.

## Explicitly out of scope for V1

Native iOS/macOS apps, multi-agent/autonomous planning systems, Gmail/Calendar write actions, Google Drive, Notion, WhatsApp, CRM, business-system integrations, recurring/conditional automations.

## Implementation phases

1. Local development environment
2. Basic Claude chat
3. Database
4. Conversation history
5. Memory
6. Agent/tool architecture
7. Web search
8. Gmail (read-only)
9. Google Calendar (read-only)
10. Tasks/reminders
11. Authentication/security hardening
12. PWA/mobile optimization
13. Deployment
14. Testing and hardening

Each phase: explain what was built, why, how to test it, and wait for confirmation before proceeding.
