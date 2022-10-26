import pandas as pd

from django.core.management.base import BaseCommand
from transactions.models import Transaction
from transactions.utils import date_from_str, decimal_from_value


class Command(BaseCommand):
    help = "Read a csv file and import the data into the database table transaction"

    def add_arguments(self, parser):
        parser.add_argument("csv_input", nargs="+", type=str)
        parser.add_argument("-o", "--csv_output", nargs="+", type=str)

    def handle(self, *args, **options):
        self.errors = []
        self.total_row_success = 0
        self.total_row_failure = 0
        self.csv_input = options["csv_input"][0]
        self.csv_output = None
        if options["csv_output"]:
            self.csv_output = options["csv_output"][0]

        self.read_csv()
        self.print_result()
        self.write_errors()

    def read_csv(self):
        self.stdout.write("File to read: " + self.csv_input)
        if self.csv_output:
            self.stdout.write("File to write: " + self.csv_output)
        df = pd.read_csv(
            self.csv_input,
            converters={"Date": date_from_str, "Amount": decimal_from_value},
        )
        df = df.reset_index()
        for index, row in df.iterrows():
            try:
                t = Transaction.create(
                    date=row["Date"], account=row["Account"], amount=row["Amount"]
                )
                t.validate_and_raise()
                t.save()
                self.total_row_success += 1
            except Exception:
                self.errors.append([row["Date"], row["Account"], row["Amount"]])
                self.total_row_failure += 1

    def print_result(self):
        self.stdout.write(
            self.style.SUCCESS(
                "Read rows: {}. Not read rows: {}".format(
                    self.total_row_success,
                    self.total_row_failure,
                )
            )
        )

    def write_errors(self):
        self.pd_errors = pd.DataFrame(
            self.errors, columns=["Date", "Account", "Amount"]
        )
        try:
            if self.csv_output:
                self.pd_errors.to_csv(
                    self.csv_output, sep=",", index=False, encoding="utf-8"
                )
        except Exception:
            pass
