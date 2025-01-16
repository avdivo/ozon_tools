from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from .services import send_message
from services.ozon.transaction import get_transaction
from services.ozon.fbo_products import get_fbo_products
from services.ozon.products_rating import products_rating
from services.ozon.utils import get_last_month_current_trimester, get_last_month_previous_trimester

from config import Config


async def show_main_menu(message: types.Message, state: FSMContext):
    """Отображение главного меню
    :param message:
    :param state:
    :return:
    """
    user_data = await state.get_data()  # Получение данных пользователя из состояния

    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Прошлые продажи"),
                types.KeyboardButton(text="Текущие продажи"),
            ],
            [
                types.KeyboardButton(text="Товары на FBO"),
            ],
            [
                types.KeyboardButton(text="Рейтинг товаров"),
            ],
        ],
        resize_keyboard=True
    )

    await message.reply("Просто жмите на имеющиеся кнопки)", reply_markup=keyboard)


async def handle_for_command(message: types.Message, state: FSMContext):
    command = message.text.lstrip('/')
    param = '*'
    out = f'Без фильтра.'
    if command == 'filter_ln':
        param = 'ln'
        out = f'Установлен фильтр {param}'
    elif command == 'filter_vk':
        param = 'vk'
        out = f'Установлен фильтр {param}'

    await state.update_data(alias=param)
    await message.reply(out)


async def handle_main_menu(message: types.Message, state: FSMContext, alias_default: str):
    """Обработка нажатий на кнопки главного меню
    :param message:
    :param state:
    :param alias: псевдоним пользователя для фильтрации товаров:
    :return
    """
    # Получаем сохраненный алиас
    data = await state.get_data()
    alias = data.get("alias", alias_default)

    if "продажи" in message.text:
        if message.text == "Прошлые продажи":
            date = get_last_month_previous_trimester()
        elif message.text == "Текущие продажи":
            date = get_last_month_current_trimester()
        else:
            return
        result = await get_transaction(date, alias)
        await send_message(message, result)

    elif message.text == "Товары на FBO":
        result = await get_fbo_products(alias)
        await send_message(message, result)

    elif message.text == "Рейтинг товаров":
        result = await products_rating(alias)
        await send_message(message, result)

    elif message.text.startswith(""):
        pass


async def start_command(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()  # Сброс состояния при старте
    await show_main_menu(message, state)  # Отображение главного меню


async def help_command(message: types.Message):
    """Обработка команды /help"""
    help_text = f"""
Набор инструментов для работы с магазином на Ozon.

Доступные команды:
/start - Начать работу с ботом.
/help - Показать справку.
/filter - Установить фильтр на артикул товара (2 последние буквы). Любые.
/filter_ln - Фильтр ln.
/filter_vk - Фильтр vk.

Кнопка "Прошлые продажи":
выведет список продаж за предыдущий квартал.

Кнопка "Текущие продажи":
выведет список продаж за текущий квартал.

Кнопка "Товары на FBO":
выведет список товаров находящихся на складах FBO

Кнопка "Рейтинг товаров":
выведет список товаров (с дополнительной информацией) которые были проданы за последнее время (2-3 месяца) в порядке убывания количества продаж.
    """
    await message.answer(help_text)


def register_handlers(router):
    """Регистрация обработчиков сообщений
    :param router:
    :return:
    """
    router.message.register(start_command, Command(commands=['start']))
    router.message.register(help_command, Command(commands=['help']))
    router.message.register(handle_main_menu, F.text.in_(["Прошлые продажи", "Текущие продажи",
                                                          "Товары на FBO", "Рейтинг товаров"]))
    router.message.register(handle_for_command, F.text.in_(["/filter", "/filter_ln", "/filter_vk"]))
