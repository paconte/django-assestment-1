from django.core.management.base import BaseCommand
from transactions.readers import CsvReader


class Command(BaseCommand):
    help = "Read a csv file and import the data into the database table transaction"

    def add_arguments(self, parser):
        parser.add_argument("csv_input", nargs="+", type=str)
        parser.add_argument("-o", "--csv_output", nargs="+", type=str)

    def handle(self, *args, **options):
        # init variables
        self.csv_input = options["csv_input"][0]
        self.csv_output = None
        if options["csv_output"]:
            self.csv_output = options["csv_output"][0]

        # print information
        self.stdout.write("File to read: " + self.csv_input)
        if self.csv_output:
            self.stdout.write("File to write: " + self.csv_output)

        # read the csv and store it in the db
        csvReader: CsvReader = CsvReader()
        csvReader.read(self.csv_input)
        csvReader.save()

        # print result of the operation to the user
        self.print_result(csvReader.rows_success, csvReader.rows_failure)

        # write a csv file with the not read rows
        if self.csv_output:
            csvReader.write_errors_to_file(self.csv_output)

    def print_result(self, rows_success: int, rows_failure: int):
        self.stdout.write(
            self.style.SUCCESS(
                "Read rows: {}. Not read rows: {}".format(
                    rows_success,
                    rows_failure,
                )
            )
        )
