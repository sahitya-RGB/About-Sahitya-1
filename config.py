import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_IDS = [int(x) for x in os.getenv("CHANNEL_IDS").split(",")]

PAID_CHANNEL = os.getenv("PAID_CHANNEL")
FOLDER_LINK = os.getenv("FOLDER_LINK")
SUPPORT_LINK = os.getenv("SUPPORT_LINK")