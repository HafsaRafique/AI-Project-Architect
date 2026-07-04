.PHONY: install run test lint eval docker-build docker-up

install:
	pip install -r requirements.txt gunicorn pytest ruff

run:
	python server.py

test:
	pytest -v

lint:
	ruff check .

eval:
	python eval/run_eval.py --repeats 3

docker-build:
	docker build -t rpg-chess .

docker-up:
	docker compose up -d
