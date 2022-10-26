from datetime import date, datetime
from decimal import Decimal, Context, Inexact


TWOPLACES = Decimal(10) ** -2


def decimal_from_value(value):
    return Decimal(value)


def date_from_str(value: str) -> date:
    return date.fromisoformat(value)


def is_future(value: date) -> bool:
    return value > datetime.today().date()


def is_max_two_decimals(value: Decimal) -> bool:
    try:
        value.quantize(TWOPLACES, context=Context(traps=[Inexact]))
    except Inexact:
        return False
    return True

def is_max_seven_digits(value: Decimal) -> bool:
    return 10_000_000 > value.quantize(0)

