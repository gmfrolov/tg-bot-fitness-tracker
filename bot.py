import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.routers import profile, progress
from app.middlewares import LoggingMiddleware

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(profile.router, progress.router)
dp.message.middleware(LoggingMiddleware())

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())