import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
    OZON_CLIENT_ID = os.getenv('OZON_CLIENT_ID')
    OZON_TOKEN = os.getenv('OZON_TOKEN')
    WEBAPP_HOST = os.getenv('WEBAPP_HOST')
    WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', 8000))

    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

    # Идентификаторы пользователей в tg для которых работает бот.
    # Для каждого указано сокращение в Артикуле, по которому можно распознать его товары.
    USERS = dict(pair.split(':') for pair in os.getenv("USERS", "").split(','))
