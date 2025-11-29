import asyncio
import logging
import os
from urllib.request import urlopen

import aiosqlite
import json_log_formatter
from pyrogram import Client

handler = logging.StreamHandler()
handler.setFormatter(json_log_formatter.JSONFormatter())

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def get_bots(db_path: str) -> list[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM bots WHERE is_active != 0") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def push_kuma(url: str, status: str = "up", msg: str = ""):
    try:
        full_url = f"{url}?status={status}&msg={msg}"
        await asyncio.to_thread(urlopen, full_url, timeout=10)
    except Exception as e:
        logger.error("Kuma push failed", extra={"url": url, "error": str(e)})


async def check_bot(client: Client, db_path: str, bot_id: int, started: set, running: set):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM bots WHERE id = ?", (bot_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return
            bot = dict(row)

    try:
        if bot_id not in started:
            await client.send_message(bot["address"], "/start")
            started.add(bot_id)
        await client.send_message(bot["address"], "/health")
        logger.info("health check ok", extra={"bot": bot["name"], "address": bot["address"]})
        if bot.get("kuma_url"):
            await push_kuma(bot["kuma_url"], "up")
    except Exception as e:
        logger.error("health check failed", extra={"bot": bot["name"], "address": bot["address"], "error": str(e)})
        if bot.get("kuma_url"):
            await push_kuma(bot["kuma_url"], "down", str(e))
    finally:
        running.discard(bot_id)


async def scheduler(client: Client, db_path: str):
    started: set[int] = set()
    running: set[int] = set()
    last_check: dict[int, float] = {}

    while True:
        bots = await get_bots(db_path)
        now = asyncio.get_event_loop().time()
        active_ids = {bot["id"] for bot in bots}

        removed = set(last_check.keys()) - active_ids
        for bot_id in removed:
            last_check.pop(bot_id, None)
            started.discard(bot_id)

        for bot in bots:
            bot_id = bot["id"]
            interval = bot["interval_seconds"]
            if bot_id in running:
                continue
            if bot_id not in last_check or (now - last_check[bot_id]) >= interval:
                running.add(bot_id)
                asyncio.create_task(check_bot(client, db_path, bot_id, started, running))
                last_check[bot_id] = now

        await asyncio.sleep(1)


async def main():
    db_path = os.environ["DATABASE_PATH"]
    session_string = os.environ["TELEGRAM_SESSION_STRING"]

    client = Client("heartbeat", session_string=session_string)

    async with client:
        await scheduler(client, db_path)


if __name__ == "__main__":
    asyncio.run(main())