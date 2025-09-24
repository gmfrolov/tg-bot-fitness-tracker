from aiogram import BaseMiddleware
from aiogram.types import Message
from app.storage import users

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id = event.from_user.id
        text = event.text or ""
        print(f"Получено сообщение: {event.text}")

        allowed_commands = ["/start", "/set_profile", "/help"]

        if not text.startswith("/"):
            return await handler(event, data)

        if text.startswith(tuple(allowed_commands)):
            return await handler(event, data)

        user = users.get(user_id)
        if not user:
            await event.answer("Ваш профиль ещё не создан!\nВведите /set_profile")
            return 

        return await handler(event, data)