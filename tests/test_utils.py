from typing import Any
from unittest.mock import patch
import pytest

import pandas as pd

from src.utils import report_to_xlsx, load_data_excel, get_fild_values_unique, load_params


@pytest.fixture
def data_input():
    return [
        {
            "Дата операции": "2020-07-05 17:11:51",
            "Дата платежа": "05.07.2020",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 300.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 300.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Переводы",
            "MCC": 0,
            "Описание": "Артем П.",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 300.0,
        },
        {
            "Дата операции": "2020-07-05 17:11:51",
            "Дата платежа": "05.07.2020",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 300.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 300.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Переводы",
            "MCC": 0,
            "Описание": "Артем П.",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 300.0,
        }
    ]

@pytest.fixture
def file_name():
    return "report.xlsx"


@report_to_xlsx()
def my_function(data_in: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(data_in)
    return df


def test_report_to_xlsx(data_input, file_name):
    my_function(data_input)
    captured = load_data_excel(file_name)
    assert captured == data_input


@pytest.fixture
def result():
    return [
        "*4556",
    ]


def test_get_fild_values_unique(data_input, result):
    assert  get_fild_values_unique(data_input, "Номер карты") == result


@pytest.fixture
def params():
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    }


def test_load_params(params):
    assert load_params("user_settings.json") == params


@patch("pandas.read_excel")
def test_load_data_excel(mock_excel_reader, data_input, file_name):
    mock_file = mock_excel_reader.return_value
    mock_file.to_dict.return_value = data_input
    assert load_data_excel(file_name) == data_input
    mock_excel_reader.assert_called_once_with(file_name)


@pytest.fixture
def file_name_err():
    return "1.xlsx"


def test_load_data_excel_err(file_name_err):
    assert load_data_excel(file_name_err) == []
