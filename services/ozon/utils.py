from datetime import datetime


def is_accept_article(article: str, alias: str) -> bool:
    """
    Совершать ли действие с товаром имеющим этот артикль.
    Алиас может быть * - совершать, ln или vk.
    Последние 2 символа артикля должны совпадать с алиасом - тогда тоже совершать.
    """
    if alias == '*':
        return True
    return article.endswith(alias)


def get_last_month_current_trimester():
    """Возвращает 15 число последнего месяца текущего триместра."""
    current_month = datetime.now().month
    current_trimester = (current_month - 1) // 3 + 1
    last_month = current_trimester * 3
    return datetime(datetime.now().year, last_month, 15)


def get_last_month_previous_trimester():
    """Возвращает 15 число последнего месяца предыдущего триместра."""
    current_month = datetime.now().month
    current_trimester = (current_month - 1) // 3 + 1

    if current_trimester > 1:
        # Предыдущий триместр в текущем году
        last_month = (current_trimester - 1) * 3
        year = datetime.now().year
    else:
        # Предыдущий триместр - 4-й триместр прошлого года
        last_month = 12
        year = datetime.now().year - 1

    return datetime(year, last_month, 15)
