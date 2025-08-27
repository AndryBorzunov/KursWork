import pandas as pd

from reports import spending_by_category
from services import individuals_transfers
from utils import load_data_excel, load_params
from views import create_json, data_select

data_input = load_data_excel("data/operations.xlsx")

# 1. Веб-страницы. Страница "Главная"
transactions = data_select(data_input, "2020.07.07 20:00:02")

params = load_params("user_settings.json")

result_list = create_json(transactions, params)

print("1. Веб-страницы. Страница 'Главная'\n")
print(result_list)
print()

# 2. Сервисы. Поиск переводов физическим лицам
print("2. Сервисы. Поиск переводов физическим лицам\n")
print(individuals_transfers(data_input))
print()

# 3. Отчеты. Траты по категории
print("3. Отчеты. Траты по категории 'Супермаркеты'")
spending_by_category(pd.DataFrame(data_input), "Супермаркеты", "2021.12.31")
