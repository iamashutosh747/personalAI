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

---

Further setup steps (database, frontend, deployment) will be added here as each phase introduces them.
