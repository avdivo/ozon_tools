from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """Состояния пользователя
    """
    waiting_for_image = State()  # Ожидание изображения
    waiting_for_language = State()  # Ожидание выбора языка
