# Возвращает информацию о том сколько и каких товаров есть на складах fbo
# Сортирует в порядке убывания количества
from fastapi import HTTPException

from app import app
from services.ozon.utils import is_accept_article


async def get_fbo_products(alias):
    """
    Вернет название товара, артикул и их количество на складах fbo.
    Текст в формате md.
    """
    # Формируем словарь product_id: количество на fbo
    endpoint = "/v4/product/info/stocks"
    payload = {
        "cursor": "",
        "filter": {},
        "limit": 1000
    }
    try:
        fbo_products = await app.state.ozon_client.make_request(endpoint, payload)
    except HTTPException as e:
        return {"error": e.detail}
    if not fbo_products["total"]:
        return "Нет товаров на складах FBO."

    # Создаем словарь
    product_count = {}  # Словарь содержит id товаров и их количество на FBO
    for item in fbo_products["items"]:
        count = None
        for stock in item["stocks"]:
            if stock["type"] == "fbo":
                count = stock["present"]
        if count:
            product_count[item["product_id"]] = count

    # Формируем выходной список словарей: Товар, артикул, количество
    if not product_count:
        return "Нет товаров на складах FBO."
    # Запрос на получение товаров чьи product_id есть в списке
    endpoint = "/v3/product/info/list"
    payload = {
        "product_id": list(product_count.keys())
    }
    try:
        products = await app.state.ozon_client.make_request(endpoint, payload)
    except HTTPException as e:
        return {"error": e.detail}

    # Собираем в сводный словарь нужную информацию
    # product_id: {name:Название товара, article: артикул, count: количество на FBO}
    products = {product["id"]: {"name": product["name"], "article": product["offer_id"],
                                "count": product_count[product["id"]]} for product in products["items"]
                if is_accept_article(product["offer_id"], alias)}

    # Сортируем словарь по количеству
    products = dict(
        sorted(products.items(), key=lambda item: item[1]["count"], reverse=True)
    )

    # Подготовка текста для вывода
    out = ''
    answer = []  # Ответ разбивается на строки длиной не более 3500 символов
    for product in products.values():
        # ---------------------------------------------------------------------------
        out += f"""
{product["name"]} ({product["article"]})
На складе: {product["count"]}

        """
        # --------------------------------------------------------------------------
        if len(out) > 3500:
            answer.append(out)
            out = ''
    if len(out):
        answer.append(out)

    return answer
