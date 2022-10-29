import datetime
import json
import pandas as pd

from decimal import Decimal
from io import BytesIO, StringIO
from unittest import TestCase

from django.core.management import call_command
from django.db.utils import IntegrityError
from django.test import TransactionTestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Transaction
from .pandas import df_to_json
from .utils import (
    date_from_str,
    decimal_from_value,
    is_future,
    is_max_two_decimals,
    is_max_seven_digits,
)


today = datetime.datetime.today().date()
csv_test_file_1 = "data/test/test1.csv"
csv_test_file_2 = "data/test/test2.csv"
csv_test_file_3 = "data/test/test3.csv"
csv_test_file_4 = "data/test/data.csv"


class TransactionModelTests(TransactionTestCase):

    reset_sequences = True

    def test_validate(self):
        t = Transaction.create(today, account=1, amount=decimal_from_value(1))
        self.assertTrue(t.validate())
        t = Transaction.create(
            date=date_from_str("2020-08-15"),
            account=1,
            amount=decimal_from_value(1000512),
        )
        self.assertTrue(t.validate())

    def test_create_transaction(self):
        """
        Ensure we can create simple transaction objects
        """
        transaction = Transaction.objects.create(date=today, account=1, amount=1000)
        self.assertEqual(transaction.pk, 1)
        transaction = Transaction.objects.create(date=today, account=2, amount=-1000)
        self.assertEqual(transaction.pk, 2)

    def test_account(self):
        """
        Ensure the db dont accept wrong account numbers
        """
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(date=today, account=-1, amount=1000)

    def test_amount(self):
        """
        Ensure the db dont accept wrong amount decimals and accept valid decimals
        """
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

        # amount = Decimal("10000000")  # 8 figures
        # with self.assertRaises(InvalidOperation):
        #    Transaction.objects.create(date=today, account=4, amount=amount)

    def test_read_csv_command_output(self):
        """
        Ensure we can import a valid csv file from CLI
        """
        out = StringIO()

        call_command("import_csv", csv_test_file_1, stdout=out)
        expected_output = "Read rows: 6. Not read rows: 6"
        self.assertIn(expected_output, out.getvalue())
        self.assertEquals(6, Transaction.objects.count())

        call_command("import_csv", csv_test_file_2, stdout=out)
        expected_output = "Read rows: 3. Not read rows: 3"
        self.assertIn(expected_output, out.getvalue())
        self.assertEquals(9, Transaction.objects.count())

        call_command("import_csv", csv_test_file_4, stdout=out)
        expected_output = "Read rows: 79999. Not read rows: 0"
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
        self.assertTrue(is_max_seven_digits(Decimal(100000)))  # 6 digits
        self.assertTrue(is_max_seven_digits(Decimal(1000000)))  # 7 digits
        self.assertTrue(is_max_seven_digits(Decimal(9999999)))  # 7 digits
        self.assertFalse(is_max_seven_digits(Decimal(10000000)))  # 8 digits


class TransactionAPITests(APITestCase):
    def test_upload_file(self):
        """
        Ensure we can upload a valid csv file
        """
        file = BytesIO()
        df = pd.read_csv(csv_test_file_1)
        df.to_csv(file, sep=",", index=False, encoding="utf-8")
        file.seek(0)
        url = reverse("upload-csv")
        response = self.client.post(url, {"file": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 6)


class BalanceAPITests(APITestCase):
    url = reverse("balance")

    def setUp(self):
        call_command("import_csv", csv_test_file_3)

    def _test_balance(self, balances):
        for b in balances:
            self.assertEqual(0.0, b["balance"])

    def test_too_many_arguments(self):
        query_url = self.url + "?year=2020&month=1&account=1&is_monthly=True"
        response = self.client.get(query_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_month_and_is_monthly(self):
        query_url = self.url + "?year=2020&month=1&is_monthly=True"
        response = self.client.get(query_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_year_balance_by_account(self):
        query_url = self.url + "?year=2020"
        response = self.client.get(query_url)
        balances = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, len(balances))
        self._test_balance(balances)

    def test_full_year_balance_for_specific_account(self):
        for i in range(100, 104):
            query_url = self.url + "?year=2020&account=" + str(i)
            response = self.client.get(query_url)
            balances = response.data["data"]

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(1, len(balances))
            self._test_balance(balances)

    def test_monthly_balances_by_account(self):
        query_url = self.url + "?year=2020&is_monthly=True"
        response = self.client.get(query_url)
        balances = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(8, len(balances))
        self._test_balance(balances)

    def test_monthly_balance_for_specific_account(self):
        for i in range(100, 104):
            query_url = self.url + "?is_monthly=True&year=2020&account=" + str(i)
            response = self.client.get(query_url)
            balances = response.data["data"]

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(2, len(balances))
            self._test_balance(balances)

    def test_monthly_balance_for_specific_month_by_account(self):
        for i in range(1, 12):
            query_url = self.url + "?is_monthly=True&year=2020&montht=" + str(i)
            response = self.client.get(query_url)
            balances = response.data["data"]

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._test_balance(balances)

    def test_monthly_balance_for_specific_month_and_specific_account(self):
        for i in range(1, 12):
            query_url = self.url + "?is_monthly=True&year=2020&month=" + str(i)
            for j in range(100, 104):
                query_url += "&account=" + str(j)
                response = self.client.get(query_url)
                if response.data.get("data", False):
                    balances = response.data["data"]
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self._test_balance(balances)


class PandasTests(TestCase):
    def test_df_to_json(self):
        result = df_to_json(pd.DataFrame([]))
        self.assertEqual(json.loads('{{"data": []}}'), result)

    def get_balance(self):
        """This test is a duplicate of BalanceAPITest"""
        pass
