from dotenv import load_dotenv
import os

from telethon import TelegramClient
from telethon.tl.functions.messages import GetDiscussionMessageRequest

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

