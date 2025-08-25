from views import data_select, get_currency, get_stocks, greeting_generate, create_json
from utils import load_data_excel, load_params
from services import individuals_transfers

greeting_str = greeting_generate()
data_input = load_data_excel("data/operations.xlsx")

# 1. Веб-страницы. Страница "Главная"
transactions = data_select(data_input, "2020.07.07 20:00:02")

params = load_params("user_settings.json")

currency_rates = get_currency(params["user_currencies"])
stock_prices = get_stocks(params["user_stocks"])

result_list = create_json(greeting_str, transactions, currency_rates, stock_prices)

print("1. Веб-страницы. Страница 'Главная'\n")
print(result_list)
print()

# 2. Сервисы. Поиск переводов физическим лицам
print("2. Сервисы. Поиск переводов физическим лицам\n")
print(individuals_transfers(transactions)) #data_input))
