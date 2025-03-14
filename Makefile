.PHONY: install test lint update-deps

default: test

install: 
	pipenv install --dev --skip-lock

test:
	PYTHONPATH=./ pytest

lint:
	find {mtr2mqtt,} -name \*.py -type f -exec pylint {} \+

update-deps:
	pipenv update --dev
	pipenv check