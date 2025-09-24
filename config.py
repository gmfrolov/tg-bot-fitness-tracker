import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")

if not OPENWEATHERMAP_API_KEY:
    raise ValueError("Переменная окружения OPENWEATHERMAP_API_KEY не установлена!")