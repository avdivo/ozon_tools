# Телеграмм бот предоставляет несколько инструментов для работы с магазином в Ozon

**Ссылка на бота: [ocr_bot](https://t.me/LenaVikaOzon_bot)**  
**Ссылка на документацию [API Ozon](https://docs.ozon.ru/api/seller/)**

## Функции
- Вся информация предоставляется адресно для пользователя 
    (для его товаров, принадлежность которых определяется по его артикулу).
- Предоставление финансовой информации (транзакции) магазина за отчетный период,
    который рассчитывается от последней выплаты Ozon.


## Описание
- Бот работает на основе фреймворка FastAPI и библиотеки aiogram.  
- Построен на основе асинхронной архитектуры.
- Использует Webhook для взаимодействия с Telegram API.

## Используемые технологии
- Python 3.12
- FastAPI (для веб-сервера)
- aiogram (для работы с Telegram API)
- uvicorn (для запуска FastAPI)

## Структура проекта
```
ocrbot/
│
├── bot/                      # Папка для логики бота
│   ├── __init__.py           # Инициализация пакета
│   ├── handlers.py           # Обработчики команд и сообщений
│   └── states.py             # Определение состояний
│
├── services/                 # Папка для внешних сервисов
│   ├── __init__.py           # Инициализация пакета
│   └── ozon/                 # Логика работы с Paddle OCR
│       ├── __init__.py       # Инициализация пакета
│       ├── client.py         # Подключение к Ozon
│       └── transaction.py    # Получение финавсовой информации (транзакции)
│
├── requirements.txt          # Зависимости проекта
├── main.py                   # Основной файл запуска приложения
├── README.md                 # Документация проекта
├── config.py                 # Конфигурация приложения
│
├── Dockerfile                 # Файл конфигурации Docker
├── docker-compose.yml         # Файл для управления многоконтейнерными приложениями
└── .env                       # Файл для переменных окружения (например, токены и настройки)
```

## Установка и запуск
1. Клонировать репозиторий
2. Создать виртуальное окружение и активировать его
3. Установить зависимости из requirements.txt
4. Создать файл .env и добавить в него переменные окружения:
    BOT_TOKEN=  
    WEBHOOK_HOST=https://4a9b-37-19-205-220.ngrok-free.app/webhook  
    WEBHOOK_PATH=/webhook  
    OZON_CLIENT_ID=  
    OZON_TOKEN=  
    WEBAPP_HOST=0.0.0.0  
    WEBAPP_PORT=8000  
    USERS=user_id_telegram:vk,user_id_telegram:ln,user_id_telegram:*  
 
    С такими настройками бот автоматически установит вебхук на адрес https://4a9b-37-19-205-220.ngrok-free.app/webhook
    (можно заметить что это адрес ngrok, который можно использовать для приема запросов из внешнего интернета на 
    локальный компьютер).  

    Настройки ngrok:  
    https://4a9b-37-19-205-220.ngrok-free.app -> http://localhost:8000  
    FastApi будет принимать запросы на url 0.0.0.0, порт 8000.
5. Запустить бота командой
    ```bash
    sudo uvicorn main:app --host 0.0.0.0 --port 80 --reload
    ```
6. После остановки сервера вебхук автоматически удалится из настроек Телеграмм
