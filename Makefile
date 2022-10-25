linters:
	cd abacum && black . && flake8 --config .flake8

makemigrations:
	cd abacum && python manage.py makemigrations transactions

migrate:
	cd abacum && python manage.py migrate

docker-run:
	docker run -it -p 8020:8020 abacum

runserver:
	cd abacum && python manage.py runserver

test:
	cd abacum && python manage.py test transactions