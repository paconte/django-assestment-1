import pandas as pd

from django.core.management.base import BaseCommand
from transactions.models import Transaction


class Command(BaseCommand):
    help = "Read a csv file and import the data into the database table transaction"

    def add_arguments(self, parser):
        parser.add_argument("file_path", nargs="+", type=str)

    def handle(self, *args, **options):
        self.errors = []
        self.total_row_success = 0
        self.total_row_failure = 0
        self.file_path = options["file_path"][0]

        self.read_csv()
        self.print_result()
        self.write_errors()

    def read_csv(self):
        self.stdout.write("File to read: " + self.file_path)
        df = pd.read_csv(self.file_path)
        df = df.reset_index()
        for index, row in df.iterrows():
            try:
                t = Transaction.create(
                    date=row["Date"], account=row["Account"], amount=row["Amount"]
                )
                t.save()
                self.total_row_success += 1
            except Exception:
                self.errors.append([row["Date"], row["Account"], row["Amount"]])
                self.total_row_failure += 1

    def print_result(self):
        self.stdout.write(
            self.style.SUCCESS(
                'Read rows: {}. Not read rows: {}'.format(
                    self.total_row_success,
                    self.total_row_failure,
                )
            )
        )

    def write_errors(self):
        self.pd_errors = pd.DataFrame(
            self.errors, columns=["Date", "Account", "Amount"]
        )
        print(self.pd_errors)
