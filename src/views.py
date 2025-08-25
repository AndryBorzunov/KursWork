import os
import requests
from datetime import datetime
import pandas as pd
from utils import get_fild_values_unique
from typing import Any

from dotenv import load_dotenv
from pandas.core.interchange.dataframe_protocol import DataFrame

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_CR = os.getenv("API_KEY_CR")


def greeting_generate() -> str:
    """ Функция возвращает строку приветствия в зависимости от текущего времени """

    time_current = datetime.now()

    if 0 <= time_current.hour < 6:
        return "Доброй ночи"

    elif 6 <= time_current.hour < 12:
        return "Доброе утро"

    elif 12 <= time_current.hour < 18:
        return "Добрый день"

    else:
        return "Добрый вечер"


def data_select(data_input: list[dict], time_param: str) -> list[dict]:
    df = pd.DataFrame(data_input)

    # Выбираем данные из диапазона времени

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    time_param = datetime. strptime(time_param, "%Y.%m.%d %H:%M:%S")
    time_param_start = time_param.replace(day=1, hour=0, minute=0, second=0)

    df_filtered = df[(df["Дата операции"] >= time_param_start) & (df["Дата операции"] <= time_param)]

    return df_filtered.to_dict(orient="records")


def get_stocks(param_in: list[str]) -> list[dict]:
    url = "https://www.alphavantage.co/query" #?function=GLOBAL_QUOTE&symbol=INTC&apikey=4ZBM2P5DRG9SRY0T"  #"https://api.api-ninjas.com/v1/sp500"

    result = []
    for param in param_in:
        params = {"function": "GLOBAL_QUOTE", "symbol": param, "apikey": API_KEY}
        #headers = {"X-Api-Key": API_KEY}
        response = requests.get(url, params)
        # if (response.status_code == 200):
        data = response.json()
        if "Global Quote" in data:
            stock_price = {"stock": data["Global Quote"]["01. symbol"], "price": data["Global Quote"]["05. price"]}
            result.append(stock_price)

    return result


def get_currency(param_in: list[str]) -> list[dict]:

    amount = 1
    url = "https://api.apilayer.com/exchangerates_data/convert"
    headers = {"apikey": API_KEY_CR}

    result = []
    for param in param_in:
        currency_code = param
        params = {"to": "RUB", "from": currency_code, "amount": amount}
        response = requests.get(url, params, headers=headers)
        # if (response.status_code == 200):
        currency_rate = {"currency": response.json()["query"]["from"], "rate": response.json()["info"]["rate"]}
        result.append(currency_rate)
        #data = response.json()
    return result #float(data["result"])


def get_cards(transactions: list[dict]) -> list[dict]:

    #print(transactions)
    cards = get_fild_values_unique(transactions, "Номер карты")
    #print(cards)

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
    df = pd.DataFrame(transactions)
    df_ok = df[df["Статус"] == "OK"]

    #top_5_transactions = df_ok["Сумма операции"].abs().nlargest(5, keep="all")

    top_5_transactions = df_ok.nlargest(5, ["Сумма операции с округлением"])
    #print(top_5_transactions)

    top_transactions = []
    for index, row in top_5_transactions.iterrows():
        transactions_dict = dict()
        transactions_dict["date"] = row["Дата платежа"]
        transactions_dict["amount"] = row["Сумма операции"]
        transactions_dict["category"] = row["Категория"]
        transactions_dict["description"] = row["Описание"]
        top_transactions.append(transactions_dict)

    return top_transactions


def create_json(greeting_str: str, transactions: list[dict], currency_rates: list[dict], stock_prices: list[dict]) -> list[Any]:
    result = []
    result_dict = dict()
    result_dict["greeting"] = greeting_str
    #result.append(greeting_dict)

    #cards_dict = {"cards": cards_list}
    result_dict["cards"] = get_cards(transactions)
    result_dict["top_transactions"] = get_top_transactions(transactions)
    result_dict["currency_rates"] = currency_rates
    result_dict["stock_prices"] = stock_prices

    result.append(result_dict)

    return result
