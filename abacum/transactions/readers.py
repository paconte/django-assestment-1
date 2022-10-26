import pandas as pd

from os import PathLike
from typing import Union
from .models import Transaction
from .utils import date_from_str, decimal_from_value


class CsvReader:
    rows_success: int = 0
    rows_failure: int = 0
    errors: list = []

    def read(self, filepath_or_buffer: Union[str, PathLike[str]]) -> pd.DataFrame:
        self.df = pd.read_csv(
            filepath_or_buffer,
            converters={"Date": date_from_str, "Amount": decimal_from_value},
        )
        return self.df

    def save(self):
        self.df = self.df.reset_index()
        for _, row in self.df.iterrows():
            try:
                t: Transaction = Transaction.create(
                    date=row["Date"], account=row["Account"], amount=row["Amount"]
                )
                t.validate_and_raise()
                t.save()
                self.rows_success += 1
            except Exception:
                self.errors.append([row["Date"], row["Account"], row["Amount"]])
                self.rows_failure += 1
        self.pd_errors = pd.DataFrame(
            self.errors, columns=["Date", "Account", "Amount"]
        )

    def write_errors_to_file(self, file: Union[str, PathLike[str]]):
        self.pd_errors.to_csv(file, sep=",", index=False, encoding="utf-8")
