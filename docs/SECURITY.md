# Security

## Principles

- Secrets (Anthropic API key, database URL, OAuth client secret, token encryption key) live only in environment variables on the backend. They are never committed to git and never sent to the frontend.
- `.env` is git-ignored. Only `.env.example` (with blank values) is committed.
- Every database row that belongs to a user is scoped by `user_id`, so data isolation holds even before multi-user support is exposed in the UI.
- Google OAuth refresh tokens are encrypted at rest before being stored.
- Gmail and Google Calendar are **read-only** in V1. No send, delete, or modify actions exist until the EXECUTE + confirmation flow is implemented and tested.
- Any future EXECUTE-level action (send email, delete, modify calendar/files) requires an explicit user confirmation round-trip before it runs. Nothing externally visible happens silently.
- All tool calls, results, approvals, and rejections are recorded in the audit log — without secrets or full sensitive payloads.
- HTTPS is required in any deployed (non-local) environment.

## Reporting a problem

This is a personal project; if you (the owner) notice a security issue while testing, stop and note it in the current phase's testing notes before continuing.
