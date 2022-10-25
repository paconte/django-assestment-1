from decimal import Decimal
from django.db import models


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
    def create(cls, date: str, account: int, amount: Decimal):
        return cls(date=date, account=account, amount=amount)
