# Формирует и возвращает список финансовых транзакций магазина.
# Поступления от продажи товаров выбираются для текущего пользователя, расходы для всех.
# В магазине артикулы товаров заканчиваются на ln или vk, в зависимости от того,
# кто смотрит - фильтруются продажи.

# Список формируется от текущей даты назад, пока не будет встречена транзакция вывода
# средств с Озона. Или пока не закончатся транзакции (пустой месяц).

from fastapi import HTTPException
from datetime import datetime, timedelta
import calendar

from app import app
from services.ozon.utils import is_accept_article


async def request_transaction(date):
    """
    Делает запрос транзакций на озон за 3 месяца, переданный и 2 предыдущих.
    Возвращает список транзакций и список sku товаров из них.
    """
    transactions = []  # Список транзакций
    skus = []  # Список sku товаров
    for i in range(3):
        # Листаем месяца назад
        year = date.year
        month = date.month - i
        i += 1
        # Обработка перехода через год
        if month <= 0:
            month += 12
            year -= 1
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])

        payload = {
            "filter": {
                "date": {
                    "from": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "to": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                },
                "operation_type": [],
                "posting_number": "",
                "transaction_type": "all"
            },
            "page": 1,
            "page_size": 1000
        }

        endpoint = "/v3/finance/transaction/list"

        try:
            transactions_dict = await app.state.ozon_client.make_request(endpoint, payload)
        except HTTPException as e:
            return {"error": e.detail}

        # Создаем список sku проданных товаров, для получения их Артикулов
        for item in reversed(transactions_dict['result']['operations']):
            if item['operation_type'] == "OperationAgentDeliveredToCustomer":
                # Это доставка товара покупателю (зачисление суммы от продажи товара)
                for sku in item['items']:
                    skus.append(sku['sku'])  # Добавляем sku всех товаров

        transactions += transactions_dict['result']['operations'][::-1]

    return transactions, skus


async def request_products(skus):
    """
    Делает запрос товаров по списку sku.
    Возвращает список словарей товаров и словарь сопоставления sku: артикул.
    """
    # Создаем словарь сопоставления sku с Артиклями
    sku_to_article = {}  # Словарь сопоставления

    # Запрос на получение товаров чьи sku есть в списке
    endpoint = "/v3/product/info/list"
    payload = {
            "sku": skus
    }

    try:
        result = await app.state.ozon_client.make_request(endpoint, payload)
    except HTTPException as e:
        return {"error": e.detail}

    # sku может быть несколько у товара, они находятся в разделе source
    for item in result.get("items", []):
        offer_id = item.get("offer_id")
        for source in item.get("sources", []):
            sku = source.get("sku")
            if sku in skus:  # Проверяем, есть ли SKU в списке
                sku_to_article[sku] = offer_id
                break

    return result, sku_to_article


async def get_transaction(date, alias):
    """
    Возвращает список транзакций в формате md.
    Для каждой дата, сумма, товары.
    Добавляет суммы расходов и доходов суммируя содержимое списка.
    """
    # Создаем список транзакций за квартал
    transactions, skus = await request_transaction(date)  # Список транзакций и Список sku товаров
    skus = list(set(skus))  # Удаляем дубликаты sku

    # Создаем словарь сопоставления sku с Артиклями
    sku_to_article = {}  # Словарь сопоставления
    if skus:
        _, sku_to_article = await request_products(skus)

    # Формирование списка вывода
    out_list = []  # Список словарей
    expenses = income = income_total = 0  # Доходы и расходы (суммы)
    for item in transactions:
        if item['operation_type'] == "Operation...":
            # TODO: проигнорировать вывод денег с озона
            continue

        if item['operation_type'] == "OperationAgentDeliveredToCustomer":
            # Это транзакция продажи товара
            products = []  # Список товаров
            # Ску подойдет любой, поскольку товары одного продавца,
            # а он нам нужен только для определения продавца
            sku = None
            for sku_ in item['items']:
                sku = sku_['sku']
                products.append(f"- {sku_['name']} (_{sku_to_article[sku]}_)")  # Добавляем sku всех товаров

            # Добавляем поля
            to_add = {}
            if is_accept_article(sku_to_article[sku], alias):
                # Этот заказ добавляется
                to_add['operation_date'] = f"{item['operation_date'][8:10]}.{item['operation_date'][5:7]}.{item['operation_date'][0:4]}"
                to_add['products'] = '\n'.join(products)
                to_add['amount'] = item['amount']  # Цена

                # Считаем сумму доходов
                income += item['amount']
                income_total += item['amount']

            else:
                income_total += item['amount']
                continue

            out_list.append(to_add)

        else:
            # Все что не есть прибыль, будем добавлять в расходы
            expenses += item['amount']

    # Подготовка сообщения
    out = ''
    answer = []  # Ответ разбивается на строки длиной не более 3500 символов
    for to_add in out_list:
# ---------------------------------------------------------------------------
        out += f"""
    *{to_add['operation_date']}  -  {to_add['amount']} RUB*
    
{to_add['products']}

"""
# --------------------------------------------------------------------------
        if len(out) > 3500:
            answer.append(out)
            out = ''
    if len(out):
        answer.append(out)

    # Блок с суммами
    out = f"""  
---------------------------
*Прибыль с продаж: {income:.2f} RUB*

*Прибыль с продаж всего по магазину: {income_total:.2f} RUB*
*Расходы всего по магазину: {expenses:.2f} RUB*
    """
    answer.append(out)

    return answer
