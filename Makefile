.PHONY: install run activate_venv deactivate_venv

install:
	pip3 install -r requirements.txt

run:
	python3 main.py

activate:
	source bin/activate

deactivate:
	deactivate

sort:
	isort . --profile black --skip lib/ --skip bin/