import json
import pandas as pd

from typing import List


def pd_balance_calculator(data: List, is_monthly: bool) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if is_monthly:
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m')
        balance = df.groupby(["account", "date"]).sum()
        df = df.merge(balance, on=["account", "date"])
        df = df.rename(columns={"amount_y": "balance"}, errors="raise")
        df = df.drop(columns={"amount_x"}).drop_duplicates()
        df = df.sort_values(["account", "date"], ascending=[True, True])
    else:
        df = df.drop(columns={"date"})
        balance = df.groupby(["account"])["amount"].sum()
        df = df.drop(columns={"amount"}).drop_duplicates()
        df = df.merge(balance, left_on='account', right_on='account')
        df = df.rename(columns={"amount": "balance"}, errors="raise")

    return df


def dataframe_to_json(df: pd.DataFrame) -> str:
    if df.empty:
        result = json.loads(f"{{\"data\": []}}")
    else:
        df_json = df.to_json(orient="records")
        result = json.loads(f"{{\"data\": [{df_json}]}}")

    return result
