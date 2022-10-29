import json
import pandas as pd

from typing import List


def get_balance(data: List[List], is_monthly: bool) -> pd.DataFrame:
    """
    Creates a pandas DataFrame containing account balances

    Parameters
    ----------
    data : List[List]
        The data to be loaded into the pandas dataframe
    is_monthly : bool
        A flag used to sort the balance by month

    Returns
    -------
    Dataframe
        A dataframe with the calculated account balances
    """
    df = pd.DataFrame(data)

    if df.empty:
        return df

    if is_monthly:
        df["date"] = pd.to_datetime(df["date"])
        df["date"] = df["date"].dt.strftime("%Y-%m")
        balance = df.groupby(["account", "date"]).sum()
        df = df.merge(balance, on=["account", "date"])
        df = df.rename(columns={"amount_y": "balance"}, errors="raise")
        df = df.drop(columns={"amount_x"}).drop_duplicates()
        df = df.sort_values(["account", "date"], ascending=[True, True])
    else:
        df = df.drop(columns={"date"})
        balance = df.groupby(["account"])["amount"].sum()
        df = df.drop(columns={"amount"}).drop_duplicates()
        df = df.merge(balance, left_on="account", right_on="account")
        df = df.rename(columns={"amount": "balance"}, errors="raise")

    return df


def df_to_json(df: pd.DataFrame) -> str:
    """
    Wraps the json output of a DataFrame with the following format:
    {
        data: json_object
    }
    """
    if df.empty:
        result = json.loads('{{"data": []}}')
    else:
        df_json = df.to_json(orient="records")
        result = json.loads(f'{{"data": {df_json}}}')

    return result
