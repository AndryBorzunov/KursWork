from typing import Any, Dict, Hashable, List
import json

import pandas as pd

from functools import wraps


def report_to_xlsx(filename: str | None = None) -> Any:
    """Декоратор для записи логов выполнения функции"""

    def wrapper(function: Any) -> Any:
        """Обертка для функции"""

        @wraps(function)
        def inner(*args: Any, **kwargs: Any) -> Any:
            """Внутренняя функция, реализующая запись лога"""

            result = None
            try:
                result = function(*args, **kwargs)
                df = pd.DataFrame(result)
                if filename:
                    df.to_excel(filename, sheet_name="Sheet1", index=False)
                    #with open(filename, "a", encoding="utf-8") as file:
                        #file.write(f"INFO: {function.__name__} ok: Inputs: {args[1]}, {args[2]}. Outputs: {result}\n")
                        #file.write(f"{result}\n")
                else:
                    df.to_excel("report.xlsx", sheet_name="Sheet1", index=False)
                    #print(f"INFO: {function.__name__} ok: Inputs: {args[1]}, {args[2]}. Outputs: {result}")
                    #print(f"{result}")
                return result
            except Exception as e:
                if filename:
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(
                            f"ERROR: {function.__name__} error: {e}. Inputs: {args[1]}, {args[2]}. Outputs: {result}\n"
                        )
                else:
                    print(f"ERROR: {function.__name__} error: {e}. Inputs: {args[1]}, {args[2]}. Outputs: {result}")
                return result

        return inner

    return wrapper


def load_data_excel(file_name: str) -> List[Dict[Hashable, Any]]:
    """Функция загружает таблицу из файла excel (.xlsx)"""

    try:
        transactions_xls = pd.read_excel(file_name)

        transactions_json = transactions_xls.to_dict(orient="records")
        return transactions_json

    except FileNotFoundError as file:
        print(f"Файл {file} не найден")
        return []


def get_fild_values_unique(data: list[dict], name_fild: str) -> List[str]:
    """
    Возвращает уникальные значения поля "description"
    """

    df = pd.DataFrame(data).loc[:name_fild]
    df = df.loc[df[name_fild].notnull()]

    result = list(df[name_fild].unique())

    return result


def load_params(file_name: str) -> Dict[str, Any]:
    """Считывание параметров, записанных в json формате из файла"""

    try:
        with open(file_name, encoding="utf-8") as file:
            transactions = json.load(file)
            if isinstance(transactions, dict):
                return transactions
            else:
                print("no json")
                return dict()
    except Exception as e:
        print(e)
        return dict()
