import datetime
from decimal import Decimal, InvalidOperation

from django.test import TransactionTestCase
from django.db.utils import IntegrityError
from django.core.management import call_command

from io import StringIO

from .models import Transaction


class TransactionModelTests(TransactionTestCase):

    reset_sequences = True
    date = datetime.datetime.today()

    def test_create_transaction(self):
        transaction = Transaction.objects.create(date=self.date, account=1, amount=1000)
        self.assertEqual(transaction.pk, 1)
        transaction = Transaction.objects.create(
            date=self.date, account=2, amount=-1000
        )
        self.assertEqual(transaction.pk, 2)

    def test_account(self):
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(date=self.date, account=-1, amount=1000)

    def test_amount(self):
        amount = Decimal("1000000")  # 7 figures
        Transaction.objects.create(date=self.date, account=1, amount=amount)

        amount = Decimal("1000000.99")  # 7 + 2 figures
        Transaction.objects.create(date=self.date, account=2, amount=amount)
        t = Transaction.objects.get(account=2)
        self.assertEqual(t.amount, amount)

        amount = Decimal("100000.999999")  # 6 + 6 figures
        Transaction.objects.create(date=self.date, account=3, amount=amount)
        t = Transaction.objects.get(account=3)
        self.assertEqual(t.amount, Decimal("100001"))

        amount = Decimal("10000000")  # 8 figures
        with self.assertRaises(InvalidOperation):
            Transaction.objects.create(date=self.date, account=4, amount=amount)

    def test_read_csv_command_output(self):
        out = StringIO()

        call_command("import_csv", "data/test/data.csv", stdout=out)
        expected_output = 'Read rows: 79999. Not read rows: 0'
        self.assertIn(expected_output, out.getvalue())

        call_command("import_csv", "data/test/test1.csv", stdout=out)
        expected_output = 'Read rows: 1. Not read rows: 1'
        self.assertIn(expected_output, out.getvalue())

