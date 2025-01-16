import logging
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request

import app
from config import Config
from bot.handlers import register_handlers
from bot.middleware import AccessMiddleware

from services.ozon.client import OzonClient


logging.basicConfig(level=logging.INFO)  # Лог файл не создается, логи выводятся в консоль

bot = Bot(token=Config.BOT_TOKEN)
router = Router()
register_handlers(router)
# Регистрация middleware для доступа пользователей по id
router.message.middleware(AccessMiddleware(allowed_users=Config.USERS))

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

app = app.app


@app.on_event("startup")
async def on_startup():
    """Установка вебхука при запуске приложения"""
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != Config.WEBHOOK_URL:
        await bot.set_webhook(Config.WEBHOOK_URL)
    logging.info(f"Webhook set to URL: {Config.WEBHOOK_URL}")

    # Создание экземпляра OzonClient
    ozon_client = OzonClient(base_url="https://api-seller.ozon.ru", client_id=Config.OZON_CLIENT_ID,
                             api_key=Config.OZON_TOKEN)
    # Инициализация клиента
    await ozon_client.startup()
    # Сохраняем экземпляр клиента в app.state
    app.state.ozon_client = ozon_client


@app.on_event("shutdown")
async def on_shutdown():
    """Удаление вебхука и закрытие хранилища при завершении работы приложения"""
    await bot.delete_webhook()
    await dp.storage.close()

    # Закрытие клиента при остановке приложения
    ozon_client = app.state.ozon_client
    await ozon_client.shutdown()


# Обработка вебхуков
@app.post(Config.WEBHOOK_PATH)
async def webhook_handler(request: Request):
    """Обработка запросов. Передача боту.
    """
    update_data = await request.json()  # Получение данных из запроса
    update = Update(**update_data)  # Создание объекта обновления
    asyncio.create_task(dp.feed_update(bot, update))  # Передача обновления боту
    return JSONResponse(content={})  # Возвращение пустого ответа


if __name__ == "__main__":
    app = FastAPI()
