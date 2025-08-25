import pandas as pd
import re


def individuals_transfers(transactions: list[dict]) -> list[dict]:
    """ Поиск переводов физическим лицам """

    df = pd.DataFrame(transactions)
    df_transfers = df[df["Категория"] == "Переводы"]

    pattern = "\\w+\\s\\w\\."

    search_datas = []
    for index, row in df_transfers.iterrows():

        item_str = str(row["Описание"])

        result = re.search(pattern, item_str, re.IGNORECASE)

        if result is None:
            continue
        else:
            search_datas.append(row.to_dict())

    return search_datas
