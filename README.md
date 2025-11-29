# tgbot-heartbeat

Minimalist Telegram bot health monitoring via Pyrogram.

## How it works

1. Reads bot list from SQLite database
2. Sends `/start` (1 time at cold container start) and `/health` commands to each bot at configured intervals
3. Pushes status to [Uptime Kuma](https://github.com/louislam/uptime-kuma) (optional)

## Setup

### 1. Generate session string

```bash
uv run python scripts/gen_session.py
```

Requires `API_ID` and `API_HASH` from https://my.telegram.org

### 2. Run

**Option A: Docker Compose**

```bash
TELEGRAM_SESSION_STRING=... docker compose up -d
```

**Option B: Build locally**

```bash
cp .env.example .env
# edit .env with your values
make build
make migrate
make run
```

### 3. Add bots to monitor

```bash
sqlite3 data/heartbeat.db "INSERT INTO bots (name, address, interval_seconds) VALUES ('My Bot', '@mybot', 60);"
```
