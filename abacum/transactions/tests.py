import datetime
from decimal import Decimal, InvalidOperation
from unittest import TestCase

from django.test import TransactionTestCase
from django.db.utils import IntegrityError
from django.core.management import call_command

from io import StringIO

from .models import Transaction
from .utils import (
    date_from_str,
    decimal_from_value,
    is_future,
    is_max_two_decimals,
    is_max_seven_digits,
)


today = datetime.datetime.today().date()


class TransactionModelTests(TransactionTestCase):

    reset_sequences = True

    def test_validate(self):
        t = Transaction.create(today, account=1, amount=decimal_from_value(1))
        self.assertTrue(t.validate())
        t = Transaction.create(
            date=date_from_str("2020-08-15"), account=1, amount=decimal_from_value(1000512)
        )
        self.assertTrue(t.validate())

    def test_create_transaction(self):
        transaction = Transaction.objects.create(date=today, account=1, amount=1000)
        self.assertEqual(transaction.pk, 1)
        transaction = Transaction.objects.create(
            date=today, account=2, amount=-1000
        )
        self.assertEqual(transaction.pk, 2)

    def test_account(self):
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(date=today, account=-1, amount=1000)

    def test_amount(self):
        amount = Decimal("1000000")  # 7 figures
        Transaction.objects.create(date=today, account=1, amount=amount)

        amount = Decimal("1000000.99")  # 7 + 2 figures
        Transaction.objects.create(date=today, account=2, amount=amount)
        t = Transaction.objects.get(account=2)
        self.assertEqual(t.amount, amount)

        amount = Decimal("100000.999999")  # 6 + 6 figures
        Transaction.objects.create(date=today, account=3, amount=amount)
        t = Transaction.objects.get(account=3)
        self.assertEqual(t.amount, Decimal("100001"))

        #amount = Decimal("10000000")  # 8 figures
        #with self.assertRaises(InvalidOperation):
        #    Transaction.objects.create(date=today, account=4, amount=amount)

    def test_read_csv_command_output(self):
        out = StringIO()

        call_command("import_csv", "data/test/test1.csv", stdout=out)
        expected_output = 'Read rows: 6. Not read rows: 6'
        self.assertIn(expected_output, out.getvalue())
        self.assertEquals(6, len(Transaction.objects.all()))

        call_command("import_csv", "data/test/test2.csv", stdout=out)
        expected_output = 'Read rows: 3. Not read rows: 3'
        self.assertIn(expected_output, out.getvalue())
        self.assertEquals(9, len(Transaction.objects.all()))

        call_command("import_csv", "data/test/data.csv", stdout=out)
        expected_output = 'Read rows: 79999. Not read rows: 0'
        self.assertIn(expected_output, out.getvalue())
        self.assertEquals(80008, len(Transaction.objects.all()))


class UtilsTests(TestCase):

    def test_is_future(self):
        tomorrow = today + datetime.timedelta(1)
        yesterday = today + datetime.timedelta(-1)

        self.assertTrue(is_future(tomorrow))
        self.assertFalse(is_future(yesterday))
        self.assertFalse(is_future(today))
        self.assertFalse(is_future(date_from_str("2020-08-15")))

    def test_is_max_two_decimals(self):
        self.assertTrue(is_max_two_decimals(Decimal(1)))
        self.assertTrue(is_max_two_decimals(Decimal(1.0)))
        self.assertTrue(is_max_two_decimals(Decimal(1.00)))

        self.assertFalse(is_max_two_decimals(Decimal(1.001)))

    def test_is_max_seven_digits(self):
        self.assertTrue(is_max_seven_digits(Decimal(100000))) # 6 digits
        self.assertTrue(is_max_seven_digits(Decimal(1000000))) # 7 digits
        self.assertTrue(is_max_seven_digits(Decimal(9999999))) # 7 digits
        self.assertFalse(is_max_seven_digits(Decimal(10000000))) # 8 digits
