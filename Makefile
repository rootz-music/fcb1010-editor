# Makefile for common developer tasks

.PHONY: lint format test run

lint:
	flake8 src/ scripts/ tests/

format:
	black src/ scripts/ tests/

test:
	python3 -m unittest discover -s tests

run:
	python3 scripts/editor.py
