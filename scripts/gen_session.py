import os
from pyrogram import Client

api_id = os.environ.get("TELEGRAM_API_ID") or input("API_ID: ")
api_hash = os.environ.get("TELEGRAM_API_HASH") or input("API_HASH: ")

with Client("session", api_id=int(api_id), api_hash=api_hash) as app:
    print("\nTELEGRAM_SESSION_STRING:")
    print(app.export_session_string())