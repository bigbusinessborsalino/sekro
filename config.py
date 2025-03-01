import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    TEMP_DIR = "./temp_downloads"
    MAX_CONCURRENT = 3
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_TIMEOUT = 30
    DOWNLOAD_TIMEOUT = 3600

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is missing!")
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
