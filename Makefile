run-ui:
	@poetry run python ./src/main.py

run-server:
	@uvicorn api.main:api --reload

create-migrations:
	@PYTHONPATH=$(PWD):$$PYTHONPATH alembic revision --autogenerate -m "$(d)"

run-migrations:
	@PYTHONPATH=$(PWD):$$PYTHONPATH alembic upgrade head
