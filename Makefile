lint: #запуск линтера
	poetry run flake8 flaskproj

migrations: #  создание миграций
	flask db migrate

migrate: #  применение миграций
	flask db upgrade