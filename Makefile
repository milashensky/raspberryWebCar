all: install setup

install:
	@pip install -Ur requirements/base.txt

setup:
	@export FLASK_APP=main.py;

start:
	@python -m flask run --host=localhost --port=8000
