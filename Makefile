# Simplify build management

.PHONY: target env update build deploy lint test format

all: target

target:
	$(info ${HELP_MESSAGE})
	@exit 0

env:
	pipenv install --dev
	pipenv requirements --dev > requirements-dev.txt
	pipenv requirements > requirements.txt

update:
	pipenv update --dev

build:
	python3 setup.py build

install:
	pip install -r requirements-dev.txt
	pip install .

deploy: build
	twine upload --verbose dist/*

lint:
	#black --check cfncli/* tests/*
	bandit -r cfncli -c bandit
	flake8 --format=pylint
	pylint cfncli

test: build
	pytest -v tests/unit tests/int

#format:
	#black cfncli/* tests/*


define HELP_MESSAGE

env
  Boostrap enviroment.

update
  Update pipenv environment.

build:
  Build dist package.

lint
  Run code quality checks.

test
  Run unittests.

format
  Format python code using Black.

build
  Build python package.

deploy
  Upload python package to pypi.

endef
