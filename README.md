# django-assestment-1
Django assestment for a backend position.

## System design
Django with Django Rest Freamework is used for the assestment.
Django contains the application called transations. This app contains the transaction model where all transaction are stored.
The views.py files contains the API endpoints logic.

The database is sqlite3, this is very handy for development but not for performance.

Docker is used to build an image with nginx as a web server.

Python version 3.10 has been used for developing the app, there is no guarantee it works with other versions.

### Transactions
For convenience the transactions are decimals with two decimals values and 7 not decimal values. There are validations performed when importing values.
Depending on the use case this values can be adjusted. Furthermore while importing a csv file, all the rows which do not pass the validation will be stored
in an out csv file that could be later on processed, see CLI Usage.

## Usage

You can run the public image which last version is 0.0.3:

    ```sh
    docker run paconte/abacum=0.0.3
    ```

You can build your own image and run it:

    ```sh
    make docker-build
    make docker-run
    ```

Alternative you can use python to run the app, but you will need to set up first your venv and install locally the libraries with pip.
You can do it by yourself or use the command:

    ```sh
    make setup
    ```

Once you have installed all the libraries with make setup, you can load the environment the next time with:

    ```sh
    source .venv/abacum/bin/activate
    ```

Once you have your environment ready start the application with:

    ```sh
    make runserver
    ```

or run your tests with:

    ```sh
    make test
    ```

## CLI usage

The django command `python manage.py import_csv` is avaibale and covers the user story 1. Some examples:

    ```
    python manage.py import_csv IN_FILE
    ```

this will import the file `IN_FILE`, and if you want to write into a separate file the rows which were not imported due to error you can run:

    ```
    python manage.py import_csv IN_FILE -o OUT_FILE
    ```

Alternative you can run make to run the same command:


    ```
    make import_csv_errors IN_FILE=data/test/test3.csv OUT_FILE=data/test/errors.csv

    or

    make import_csv_errors IN_FILE=data/test/test3.csv
    ```

Be aware this will only run in your local computer once you have set your python working environment. Another option is to log in into the container image and run the command inside the container, however you need to figure out how to access the csv that you want to import, for example with a docker volume.

After importing csv files in your local computer, you can reset the databse with:

    ```
    make reset-db
    ```

this will delete your database and create a new one.

## API usage
After starting the docker container you can access the API at:

    ```
    http://0.0.0.0:8020
    ```

There are two endpoints available. The first one covers the user story 2:

    ```
    http://0.0.0.0:8020/transactions/upload/
    ```

where you can send a file for example with this code:

    ```
    response = self.client.post(
        url,
        {'file': file},
        format='multipart'
    )
    ```

or visit the URL and upload a file via form.


The second covers tthe user story 3:

    http://0.0.0.0:8020/transactions/balance/


You will need to specify the year, for example:

    ```
    http://0.0.0.0:8020/transactions/balance/&year=2020
    ```
Otherwise the default year is the current one.


If you want to access the balance for a month:

    ```
    http://0.0.0.0:8020/transactions/balance/&year=2020&month=5
    ```

If you want to access the balance for an account:

    ```
    http://0.0.0.0:8020/transactions/balance/&year=2020&account=1234

    ```
or adding the month as well:

    ```
    http://0.0.0.0:8020/transactions/balance/&year=2020&month=5&account=1234
    ```

Last you can access the monthly balance with the is_monthly flag:

    ```
    http://0.0.0.0:8020/transactions/balance/&year=2020&is_monthly=True

    or

    http://0.0.0.0:8020/transactions/balance/&year=2020&is_monthly=True&account=1234
    ```

# Live example
The application is deployed on the internet. You can see it the endpoint here:

http://195.201.148.68:8020/transactions/upload/

http://195.201.148.68:8020/transactions/balance/

Please be aware there is no ssl and the django config is still with dev settings.