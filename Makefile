.PHONY: install test

default: test

install: 
	pipenv install --dev --skip-lock

test:
	PYTHONPATH=./ pytest

lint:
	find {mtr2mqtt,tests} -name \*.py -type f -exec pylint {} \+