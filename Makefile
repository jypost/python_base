PYTHON = PYTHONPATH=. poetry run python

.PHONY: run

run:
	$(PYTHON) main.py
