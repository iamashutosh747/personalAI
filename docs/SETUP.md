# Setup

## Phase 1 — Local development environment (Windows)

Install these tools, then clone this repository and check out the project branch. Detailed step-by-step instructions with exact commands are given to the project owner in-session for each phase; this file tracks the durable reference version.

### Required tools

1. **Git for Windows** — version control, needed to get code from GitHub onto your PC.
2. **Python 3.12+** — runs the backend.
3. **Node.js LTS** — runs the frontend (needed starting Phase 2/12).
4. **Visual Studio Code** (recommended) — code editor.

### Verify installation

```
git --version
python --version
node --version
npm --version
```

Each should print a version number, not an error.

### Get the code

```
git clone https://github.com/iamashutosh747/personalAI.git
cd personalAI
git checkout claude/personal-ai-agent-v1-y6qq3b
```

### Backend Python environment

```
cd backend
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt once activated.

### Environment variables

Copy `.env.example` to `.env` in the project root and fill in real values as each phase requires them. Never commit `.env`.

Note: on some Windows setups, the plain `python` command is intercepted by an unrelated Python Launcher/Install Manager conflict. If `python --version` fails but you can open Python from the Start menu, use `py` in place of `python` for every command in this guide — they are equivalent.

## Phase 2 — Basic Claude chat

### Get an Anthropic API key

1. Go to https://console.anthropic.com/ and sign in (or create an account).
2. Open the "API Keys" section and create a new key.
3. Copy it — you won't be able to view it again after leaving the page.

### Configure `.env`

In the project root (`personalAI/`, not `personalAI/backend/`):

```
copy .env.example .env
```

Open `.env` in a text editor and paste your key after `ANTHROPIC_API_KEY=`. Leave `CLAUDE_MODEL_MAIN` and `CLAUDE_MODEL_UTILITY` as they are — these control which Claude model is used, without any model name hard-coded in the application code.

### Install backend dependencies

With `(venv)` active, from the `backend` folder:

```
pip install -r requirements.txt
```

### Run the backend

From the project root (`personalAI/`), with `(venv)` still active:

```
uvicorn backend.api.main:app --reload --port 8000
```

### Test it

Open http://127.0.0.1:8000/docs in your browser (FastAPI's built-in interactive test page).

1. Try `GET /health` → "Try it out" → "Execute". Expect `{"status": "ok", "environment": "development"}`.
2. Try `POST /api/chat` → "Try it out" → enter `{"message": "Hello, are you working?"}` → "Execute". Expect a real reply from Claude in the response body.

## Phase 3 — Database (Supabase Postgres)

### Create a Supabase project

1. Go to https://supabase.com/ and sign up (GitHub sign-in is fine).
2. Click "New Project".
3. Pick a name (e.g. `personal-ai`), set a database password — **save it somewhere**, it's needed for the connection string and Supabase won't show it again — pick a region, and create the project. Wait ~1-2 minutes for provisioning.

### Enable pgvector (used starting Phase 5)

In the project dashboard: Database → Extensions (left sidebar) → search "vector" → enable it. One-time step, saves revisiting this later.

### Get the connection string

Project Settings (gear icon) → Database → "Connection string". Use the **Session pooler** connection string (not "Direct connection") — it works reliably from any home network. Copy the URI and replace `[YOUR-PASSWORD]` with the password you set above.

### Configure `.env`

Paste the connection string after `DATABASE_URL=` in `.env`. The app automatically adjusts the driver prefix, so paste it exactly as Supabase gives it (starting with `postgresql://`).

### Install the new dependency and restart

```
pip install -r requirements.txt
```

Then restart the server (`Ctrl+C`, then re-run `uvicorn backend.api.main:app --reload --port 8000`).

### Test it

At http://127.0.0.1:8000/docs, try `GET /health/db` → "Try it out" → "Execute". Expect `{"status": "ok"}`.

## Phase 4 — Conversation history

### Pull the code and configure `.env`

```
git pull origin claude/personal-ai-agent-v1-y6qq3b
notepad .env
```

Set `OWNER_EMAIL` to your own email address (this seeds your one account — real login comes in Phase 11). Save and close.

### Restart the server

```
uvicorn backend.api.main:app --reload --port 8000
```

On startup, the app automatically creates the `users`, `conversations`, and `messages` tables in your Supabase database — no manual SQL needed.

### Test it

At http://127.0.0.1:8000/docs:

1. `POST /api/chat` with `{"message": "My favorite color is blue. Remember that."}` and no `conversation_id`. Note the `conversation_id` in the response.
2. `POST /api/chat` again, this time including that same `conversation_id`, with `{"message": "What's my favorite color?", "conversation_id": "<paste it here>"}`. Claude should correctly answer "blue" — proving it now has real conversation memory within a thread.
3. `GET /api/conversations` — should list the conversation you just created.
4. `GET /api/conversations/{conversation_id}/messages` — should list all 4 messages (2 user, 2 assistant) in order.

---

Further setup steps (frontend, deployment) will be added here as each phase introduces them.
