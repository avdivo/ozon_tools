from aiogram import BaseMiddleware
from aiogram.types import Message

class AccessMiddleware(BaseMiddleware):
    """Доступ пользователей к боту по id"""
    def __init__(self, allowed_users: dict):
        super().__init__()
        self.allowed_users = allowed_users

    async def __call__(self, handler, event: Message, data: dict):
        user_id = str(event.from_user.id)
        if user_id not in self.allowed_users:
            await event.answer("У вас нет доступа.")
            # Прерываем выполнение, выбрасывая исключение
            raise RuntimeError("Access denied")
        data['alias_default'] = self.allowed_users[user_id]  # Передача псевдонима пользователя в хендлер
        return await handler(event, data)
