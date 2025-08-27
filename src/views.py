import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from typing import Any, Dict

from utils import get_fild_values_unique

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/views.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s : %(filename)s : %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_CR = os.getenv("API_KEY_CR")


def greeting_generate(hour_in: int) -> str:
    """Функция возвращает строку приветствия в зависимости от текущего времени"""

    if 0 <= hour_in < 6:
        logger.info("greeting: 'Доброй ночи'")
        return "Доброй ночи"

    elif 6 <= hour_in < 12:
        logger.info("greeting: 'Доброе утро'")
        return "Доброе утро"

    elif 12 <= hour_in < 18:
        logger.info("greeting: 'Добрый день'")
        return "Добрый день"

    else:
        logger.info("greeting: 'Добрый вечер'")
        return "Добрый вечер"


def data_select(data_input: list[dict], time_param: str) -> list[dict]:
    """
    Выборка данных по диапазону времени операции
    :param data_input: все транзакции
    :param time_param: время, по которое необходимо выбрать данные
    :return: отфильтрованные по дате операции транзакции
    """

    df = pd.DataFrame(data_input)

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    time_param_end = datetime.strptime(time_param, "%Y.%m.%d %H:%M:%S")
    time_param_start = time_param_end.replace(day=1, hour=0, minute=0, second=0)

    df_filtered = df[(df["Дата операции"] >= time_param_start) & (df["Дата операции"] <= time_param_end)]

    logger.info(f"Время для запроса: {time_param}, количество записей: {df_filtered.shape}")

    return df_filtered.to_dict(orient="records")


def get_stock(stock: str) -> dict:
    """
    Функция запрашивает стоимость акций у стороннего сервиса через API
    :param stock: наименование акции
    :return: результат запроса
    """
    url = "https://www.alphavantage.co/query"  # "https://api.api-ninjas.com/v1/sp500"

    params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": API_KEY}
    # headers = {"X-Api-Key": API_KEY}
    response = requests.get(url, params)
    # if (response.status_code == 200):
    logger.info(f"Результат запроса {stock}: {response.status_code}")
    data = response.json()
    if "Global Quote" in data:
        stock_price = {"stock": data["Global Quote"]["01. symbol"], "price": data["Global Quote"]["05. price"]}
        return stock_price
    else:
        logger.error(data)
        return {}


def get_currency(currency_code: Any) -> dict:
    """
    Функция запрашивает стоимость валют у стороннего сервиса через API
    :param currency_code: список валют, стоимость которых надо узнать
    :return: результат запроса
    """

    url = "https://api.apilayer.com/exchangerates_data/convert"
    headers = {"apikey": API_KEY_CR}

    params = {"to": "RUB", "from": currency_code, "amount": 1}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    # if response.status_code != 200:
    #    logger.error(f"Ошибка запроса {currency_code}: {response.status_code}")
    #    return {}
    # else:
    currency_rate = {"currency": data["query"]["from"], "rate": data["info"]["rate"]}
    logger.info(f"Результат запроса {currency_code}: {currency_rate}")

    return currency_rate


def get_cards(transactions: list[dict]) -> list[Dict[str, Any]]:
    """
    Функция анализирует операции по каждой карте - вычисляет сумму всех операций по карте и кэшбэк
    :param transactions: транзакции
    :return: результат обработки данных
    """

    cards = get_fild_values_unique(transactions, "Номер карты")

    logger.info(f"Список используемых карт {cards}")

    df = pd.DataFrame(transactions)

    cards_list = []
    for card in cards:
        card_dict = {"last_digits": card[1:]}
        df_card = df[(df["Номер карты"] == card)]
        total_spent = df_card["Сумма операции"].sum()
        card_dict["total_spent"] = total_spent
        card_dict["cashback"] = round(round(total_spent, 0) / 100, 2)

        cards_list.append(card_dict)

    return cards_list


def get_top_transactions(transactions: list[dict]) -> list[dict]:
    """
    Функция определяет 5 транзакций с самой большой суммой операции
    :param transactions: транзакции
    :return: результат обработки данных
    """
    df = pd.DataFrame(transactions)
    df_ok = df[df["Статус"] == "OK"]

    top_5_transactions = df_ok.nlargest(5, ["Сумма операции с округлением"])

    top_transactions = []
    for index, row in top_5_transactions.iterrows():
        transactions_dict = dict()
        transactions_dict["date"] = row["Дата платежа"]
        transactions_dict["amount"] = row["Сумма операции"]
        transactions_dict["category"] = row["Категория"]
        transactions_dict["description"] = row["Описание"]
        top_transactions.append(transactions_dict)

    print(top_transactions)

    return top_transactions


def create_json(transactions: list[dict], params: dict) -> str:
    """
    Функция формирует данные для передачи в json формате
    :param transactions: данные о транзакциях
    :param params: стоимость валют
    :return: json строка
    """

    result_dict = {}

    # Приветствие
    time_current = datetime.now()
    result_dict["greeting"] = greeting_generate(time_current.hour)

    # Сумма операций по картам
    result_dict["cards"] = str(get_cards(transactions))

    # Пять операций с самыми большими суммами
    result_dict["top_transactions"] = str(get_top_transactions(transactions))

    # Курсы валют
    currency_rates = []
    for currency in params["user_currencies"]:
        currency_rate = get_currency(currency)
        currency_rates.append(currency_rate)

    result_dict["currency_rates"] = str(currency_rates)

    # Стоимость акций на S&P500
    stock_prices = []
    for stock in params["user_stocks"]:
        stock_price = get_stock(stock)
        stock_prices.append(stock_price)

    result_dict["stock_prices"] = str(stock_prices)

    logger.info(f"Сформированный json: {result_dict}")

    return json.dumps(result_dict)
