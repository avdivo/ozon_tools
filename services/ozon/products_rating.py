# Составляет и выводит рейтинг товаров. Рейтинг составляется из продаж.
# Собираются продажи за последние 2-3 месяца и представляются в порядке убывания частоты продаж.
# Для каждого товара выводится название, артикул, цена, количество продаж,
# количество на складе FBO, показатели оборачиваемости из отчета
# показатели оборачиваемости из отчета:
# - Среднесуточное количество проданных (ads)
# - Остаток товара (current_stock)
# - На сколько дней хватит товара (idc)
# - Уровень оборачиваемости (turnover_grade):
#       GRADES_NONE — ожидаются поставки;
#       GRADES_NOSALES — нет продаж;
#       GRADES_GREEN — хороший;
#       GRADES_YELLOW — средний;
#       GRADES_RED — плохой;
#       GRADES_CRITICAL — критический.
from datetime import datetime
from collections import Counter

from app import app
from services.ozon.utils import is_accept_article
from .transaction import request_transaction, request_products


async def products_rating(alias):
    """
    Составляется сборный отчет по товарам продававшимся за последнее время.
    Рейтинг строится исходя из количества продаж.
    Дополняется информацией: название, артикул, цена, количество продаж,
    количество на складе FBO, показатели оборачиваемости из отчета (если они получены).
    """
    # Получаем информацию о продажах
    date = datetime.now()
    _, skus = await request_transaction(date)  # Список транзакций и Список sku товаров

    # Создаем словарь sku: количество продаж (упоминаний в списке)
    skus_rating = Counter(skus)

    # Создаем словарь сопоставления sku с Артиклями и получаем информацию о товарах по sku
    products = {}  # Товары
    if skus:
        products, _ = await request_products(skus)

    # Для поиска в продуктах преобразуем в словарь с ключами sku
    # Одновременно находим в разделе stocks информацию об fbo для товара
    # и заменяем весь раздел на количество товаров на fbo
    products_dict = {}
    for product in products["items"]:
        # В разделе sources продукта ищем sku
        # Он в любом случае должен быть одним из skus,
        # ведь по этому списку выбирались товары. Но проверим.
        sku = None
        for source in product["sources"]:
            if source["sku"] in skus:
                sku = source["sku"]
        if sku:
            products_dict[sku] = product

            # Поиск количества товара на fbo
            fbo = 0
            for stock in product["stocks"]["stocks"]:
                if stock["sku"] == sku and stock["source"] == "fbo":
                    fbo = stock["present"]
            product["stocks"] = fbo

    # Собираем информацию об оборачиваемости товаров, тех, по которым она есть
    endpoint = "/v1/analytics/turnover/stocks"
    payload = {
        "sku": list(skus_rating.keys())
    }

    try:
        result = await app.state.ozon_client.make_request(endpoint, payload)
    except Exception:
        result = None

    # Преобразуем список в словарь с ключом по sku, чтобы легче находить данные
    product_turnover = {}
    if result:
        for item in result['items']:
            key = item['sku']
            del item['sku']
            product_turnover[key] = item

    # Составление отчета из имеющихся данных в формате md
    grades = {
        "GRADES_NONE": "ожидаются поставки",
        "GRADES_NOSALES": "нет продаж",
        "GRADES_GREEN": "хороший",
        "GRADES_YELLOW": "средний",
        "GRADES_RED": "плохой",
        "GRADES_CRITICAL": "критический",
    }
    out = ''
    answer = []  # Ответ разбивается на строки длиной не более 3500 символов
    for sku, count in skus_rating.most_common():
        if not is_accept_article(products_dict[sku]["offer_id"], alias):
            continue
        turnover = ''
        if sku in product_turnover:
# ---------------------------------------------------------------------------
            turnover = f"""
Среднесуточное количество продаж: {product_turnover[sku]["ads"]}
Остаток товара: {product_turnover[sku]["current_stock"]}
На сколько дней хватит товара: {product_turnover[sku]["idc"]}
Уровень оборачиваемости: {grades[product_turnover[sku]["turnover_grade"]]}
            """
# --------------------------------------------------------------------------
        out += f"""
{products_dict[sku]["name"]} ({products_dict[sku]["offer_id"]})
Цена: {products_dict[sku]["price"]}   Продаж: {count}
На FBO: {products_dict[sku]["stocks"]}
{turnover}
-----------------------
                """
# --------------------------------------------------------------------------
        if len(out) > 3500:
            answer.append(out)
            out = ''
    if len(out):
        answer.append(out)

    return answer