import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DB_NAME = Path(__file__).parent / os.getenv('DB_NAME')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASS = os.getenv('MAIL_PASS')