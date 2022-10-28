shell:
	cd abacum && python manage.py shell

linters:
	cd abacum && black . && flake8 --config .flake8

makemigrations:
	cd abacum && python manage.py makemigrations transactions

migrate:
	cd abacum && python manage.py migrate

collectstatic:
	cd abacum && python manage.py collectstatic -c

docker-run:
	docker run -it -p 8020:8020 abacum

docker-build:
	docker build . -f ./Dockerfile -t abacum

runserver:
	cd abacum && python manage.py runserver

test:
	cd abacum && python manage.py test transactions

import_csv:
# examples:
# make import_csv IN_FILE=data/test/data.csv
	cd abacum && python manage.py import_csv $(IN_FILE)

import_csv_errors:
# examples:
# make import_csv IN_FILE=data/test/test1.csv -o data/errors1.csv
	cd abacum && python manage.py import_csv $(IN_FILE) -o $(OUT_FILE)

delete_db:
	rm abacum/db.sqlite3

reset_db: delete_db migrate
