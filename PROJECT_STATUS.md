# Project Status — Career Intelligence Platform

> Living status doc for picking up this project in a new chat session. Update this whenever significant work lands.

See also: `STUDY_GUIDE.md` in this same local folder (gitignored, NOT in the public repo on purpose — it's personal interview-prep material) — a full end-to-end explainer of every concept used in this project, written so the user can defend it in an interview and rebuild something similar from scratch.

## Where things live

- **Repo**: `C:\Users\ssahi\OneDrive\Desktop\JOB PREP\SDE_PROJECTS\AI_RESUME\resume_tailor_app` (note: NOT the `SDE PREP` path — that was a wrong-folder mistake early on, the real project is under `JOB PREP`)
- **GitHub**: https://github.com/Sahilhamids/ai-resume-tailor-v2 (public repo, `main` branch)
- **Live deploy**: https://ai-resume-tailor-v2.onrender.com (Render free web service, Docker runtime)
- **Database**: Supabase Postgres (free tier), accessed via the **session/transaction pooler** (`aws-1-ap-northeast-1.pooler.supabase.com:6543`), NOT the direct `db.*.supabase.co` host — that one doesn't resolve from many networks/Render.

## Stack

- **Backend**: FastAPI + SQLAlchemy, JWT auth (`auth.py`), rate limiting via `slowapi`
- **Frontend**: React + Vite (`frontend/`), built to `static_dist/` and served by FastAPI (not a separate service)
- **DB**: PostgreSQL on Supabase, via `psycopg` v3 (NOT `psycopg2` — no prebuilt wheels for newer Python on this machine)
- **AI**: Google Gemini (primary) → Groq/Llama-3.1 (fallback), in `ai_agent.py`
- **Deploy**: Single `Dockerfile` (multi-stage: Node build → Python runtime), `render.yaml` configures Render's free Docker web service

## History / how we got here

1. Started as a Streamlit SaaS app (bcrypt auth, SQLite, single-file `app.py`). Found in the wrong folder initially (`SDE PREP`) — real repo was `JOB PREP`.
2. **Migrated to FastAPI + React + Postgres** (commit `ab9ddb3`) — full rewrite, `app.py` initially kept then later deleted once fully superseded.
3. **Removed login requirement** (commit `76da421`) — auto-issued anonymous JWT sessions so the app works with zero signup friction. Added rate limiting (5/min per IP) on AI endpoints since there's no auth gate to protect API quota.
4. **Added competitive features** (commit `1c068ff`): 3 resume templates with live preview, PDF+DOCX export, saved resume versions, AI cover letter generation, job application Kanban tracker, before/after score comparison, lightweight self-hosted analytics (`usage_events` table, no third-party service).
5. **Cleanup pass** (commit `359cb72`): deleted dead Streamlit-era files (`app.py`, `.streamlit/`, `.devcontainer/`, `sitemap.xml`, `dummy_resume.pdf`), rewrote `readme.md`, added `window.confirm()` before destructive actions (saved-resume/cover-letter/job-application deletes, "Start New Session").
6. **Added optional login + account deletion + About page** (commit `bec196c`): `POST /auth/link-account` lets a user attach email/password to their anonymous session for cross-device access; `DELETE /account` cascades a full account wipe; new `/account` and `/about` pages in the React app.

## Known gotchas (don't re-discover these)

- **Supabase pooler required**: the direct connection host doesn't resolve reliably; always use the pooler string. Port 6543 = transaction mode, which needs `connect_args={"prepare_threshold": None}` in `db.py`'s `create_engine` call (psycopg3 server-side prepared statements break under PgBouncer transaction pooling). This is already handled — don't remove it.
- **`psycopg[binary]` not `psycopg2-binary`**: this dev machine runs Python 3.14, which has no prebuilt `psycopg2-binary` wheels. `psycopg` v3 does. Already pinned correctly in `requirements.txt`.
- **`requirements.txt` encoding**: was originally corrupted as UTF-16 (garbled). Fixed via `cat > file << 'EOF'` heredoc in bash, NOT the Write tool (Write tool was observed preserving stale UTF-16 encoding once — if this happens again, recreate via bash heredoc).
- **Render needs Docker runtime**, not the native Python buildpack — Node is required to build the React frontend, and Render's Python buildpack doesn't have Node. `render.yaml` already sets `runtime: docker`.
- **Render env vars** (set manually in dashboard, never committed): `API_KEY` (Gemini), `GROQ_API_KEY`, `DATABASE_URL` (Supabase pooler string with `%40`-encoded password if it contains `@`), `JWT_SECRET`.
- **`.gitignore`** covers `*.db`, `*.pdf`, `*.docx`, `.env`, `venv/`, `frontend/node_modules/`, `static_dist/`. `.streamlit/secrets.toml` is also ignored (folder itself was later deleted entirely since Streamlit is gone).
- **Local dev**: Node.js LTS was installed via `winget install OpenJS.NodeJS.LTS` on this machine. Python venv lives at `resume_tailor_app/venv` (recreate with `python -m venv venv` if it ever points at a stale path — this happened once when the project was first found in the wrong folder).
- **PowerShell PATH**: each new PowerShell tool call needs `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")` prepended to see `node`/`npm`, since PATH changes from `winget install` don't propagate to already-open shells.
- **Local preview/testing**: use `mcp__Claude_Preview__*` tools with a `.claude/launch.json` in the **primary working directory** (`SDE PREP` path per environment config, NOT the actual repo path) pointing `runtimeExecutable` at `venv/Scripts/python.exe` and `runtimeArgs` at a small `run_preview.py` wrapper script (not committed — recreate as needed, it just sets `DATABASE_URL` to local sqlite and runs uvicorn on port 8000).

## Data model (Postgres tables)

`users`, `profiles`, `employment_history`, `skills`, `audits`, `projects`, `custom_sections`, `saved_resumes`, `cover_letters`, `job_applications`, `usage_events` — all defined in `db.py`, CRUD in `database.py`.

## Open items / not yet done

- Custom sections (certifications/awards) have backend CRUD but **no frontend UI** — never built out, low priority.
- No automated test suite — all verification so far has been manual (curl smoke tests + browser preview tool checks) before each push.
- LinkedIn import was explicitly ruled out (no free/legal way — ToS + no public API for this use case).
- API keys (Gemini/Groq) were at one point exposed in `.streamlit/secrets.toml` history before that folder was deleted — user was advised to rotate them; unconfirmed whether rotation actually happened. Worth double-checking if anything seems off with API access.
- Rate limits are currently a blanket 5/min per IP shared across `/resume/build`, `/resume/audit`, `/profile/onboard-from-pdf`, `/cover-letter/generate` — may need per-endpoint tuning once real usage patterns are visible.

## Conventions established in this project

- User has given **full permissions** for this project — proceed with destructive-feeling-but-reversible actions (file deletes, pushes to `main`) without re-asking, but still explain what's being done.
- Direct pushes to `main` are fine once explicitly confirmed by name once; no PR workflow has been requested.
- Free-tier-only constraint: every service choice (Render, Supabase, Gemini/Groq free tiers) must stay free — flag anything that would require a paid plan.
