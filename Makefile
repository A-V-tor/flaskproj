lint: #запуск линтера
	poetry run flake8 flaskproj

migrations: #  создание миграций
	flask db migrate -m'migration'

migrate: #  применение миграций
	flask db upgrade

network: # проброс наружу
	flask run --host=0.0.0.0