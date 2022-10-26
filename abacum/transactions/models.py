from decimal import Decimal
from typing import TypeVar
from django.db import models

from .utils import is_max_two_decimals, is_future, is_max_seven_digits


Trx = TypeVar("Trx", bound="Transaction")


class Transaction(models.Model):
    """
    Model to store the below csv content:

    "Date,Account,Amount"
    2020-08-15,68100000,-60512.99
    2020-10-26,52000012,176450.62
    ...
    """

    date = models.DateField()
    account = models.PositiveBigIntegerField(db_index=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    @classmethod
    def create(cls, date: str, account: int, amount: Decimal) -> Trx:
        return cls(date=date, account=account, amount=amount)

    def validate_and_raise(self) -> None:
        if not is_max_two_decimals(self.amount):
            raise ValueError("Amount has more than two decimals")
        if not is_max_seven_digits(self.amount):
            raise ValueError("Amount has more than seven integer digits")
        if is_future(self.date):
            raise ValueError("Date is in the future")

    def validate(self) -> bool:
        try:
            self.validate_and_raise()
        except ValueError:
            return False
        return True
