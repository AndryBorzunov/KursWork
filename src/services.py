import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/services.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s : %(filename)s : %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def individuals_transfers(transactions: list[dict]) -> list[dict]:
    """Поиск переводов физическим лицам"""

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

    logger.info(f"Найдено записей: {len(search_datas)}")
    logger.info(search_datas)

    return search_datas
