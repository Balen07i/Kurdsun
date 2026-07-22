# Kurdish Utility Bot

A Telegram bot built on a plugin architecture: every tool is a self-contained
module under `bot/tools/`, wired into the bot via a central registry. Heavy
work (downloads, OCR, AI calls) runs on a Celery worker so the bot stays fast.

## Currently implemented tools
- 📥 TikTok Downloader
- 🔎 Image → Text (OCR, Kurdish + English)
- 📚 Lecture Summarizer (AI-powered)

## Project layout
```
bot/
  core/        # config, db, i18n, keyboards, middleware, shared handlers - no tool logic here
  tools/       # one folder per tool: handlers.py (Telegram) + service.py (pure logic)
  worker/      # Celery app + tasks that glue services to Telegram delivery
scripts/
  init_db.py   # creates DB tables
```

## Setup

1. Copy the env template and fill in your secrets:
   ```
   cp .env.example .env
   ```
   You need: a `BOT_TOKEN` from @BotFather, and an `ANTHROPIC_API_KEY` for the summarizer.

2. Start everything with Docker Compose:
   ```
   docker compose up --build
   ```
   This starts Postgres, Redis, the bot, and the Celery worker.

3. On first run, create the database tables (in a new terminal):
   ```
   docker compose exec bot python -m scripts.init_db
   ```

4. Message your bot on Telegram with `/start`.

## Running locally without Docker (dev only)
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Run Postgres + Redis yourself (or docker compose up postgres redis)
python -m scripts.init_db
python -m bot.main                                  # terminal 1
celery -A bot.worker.celery_app worker --loglevel=INFO   # terminal 2
```

You'll also need `tesseract-ocr` and `ffmpeg` installed locally for OCR and TikTok downloads to work outside Docker.

## Adding a new tool
1. Create `bot/tools/<your_tool>/{handlers.py, service.py}`.
2. Add one `ToolInfo` entry to `bot/tools/registry.py` (this alone updates the menu).
3. Add Kurdish strings to `bot/core/i18n/ku.py`.
4. If the tool needs background processing, add a Celery task in `bot/worker/tasks.py` following the existing pattern.
5. Register the router with one line in `bot/main.py`.

Nothing else needs to change - this is the whole point of the plugin structure.

## Deploying on Railway

This project needs **two Railway services from the same repo** — one running
the bot (long-polling Telegram), one running the Celery worker — plus
Railway's Postgres and Redis plugins.

**Important:** this repo must build via the `Dockerfile`, not Railway's
Nixpacks auto-detection. Nixpacks doesn't know to install `tesseract-ocr` or
`ffmpeg`, which OCR and the TikTok downloader both depend on. The included
`railway.json` forces the Dockerfile builder — make sure it's committed to
the repo root.

Steps:
1. Add Postgres and Redis from Railway's plugin marketplace to the project.
2. Create **Service A ("bot")** from this repo.
   - Settings → Build: confirm the builder shows "Dockerfile" (from `railway.json`). If it still shows Nixpacks, set it manually to Dockerfile.
   - Settings → Deploy → Start Command: set explicitly to `python -m bot.main`. **This dashboard field always overrides the Dockerfile's `CMD` if Railway had auto-detected something before** — that's what caused the `/app/main.py` error, so don't leave it blank/inherited if it was previously auto-filled.
   - Variables: copy everything from `.env.example`, using Railway's Postgres/Redis reference variables for `DATABASE_URL` / `REDIS_URL`.
3. Create **Service B ("worker")** from the *same* repo.
   - Same Dockerfile builder.
   - Settings → Deploy → Start Command: `celery -A bot.worker.celery_app worker --loglevel=INFO --concurrency=2`
   - Same environment variables as the bot service.
4. Run the one-off table creation once, from either service's shell (Railway → service → "Command"): `python -m scripts.init_db`

If a Start Command was auto-filled by Railway before you added `railway.json`, re-check it after redeploying — Railway sometimes keeps the old detected value cached in the service settings until you edit it manually.

## Notes on production-readiness
- **Rate limiting:** free users get `FREE_DAILY_LIMIT` uses per tool per day (see `bot/core/quota.py`); a short-window anti-spam throttle also runs on every update.
- **Reliability:** every job is tracked in the `jobs` table (`pending → processing → done/failed`), and every attempt is recorded in `usage_logs` for analytics and monetization.
- **Migrations:** `scripts/init_db.py` is a quick-start table creator. For a real production deploy, switch to Alembic migrations once the schema needs to evolve without dropping data.
- **Kurdish OCR:** the Docker image installs `tesseract-ocr-kur`; if that language pack isn't available in your environment, OCR automatically falls back to English-only rather than crashing.
