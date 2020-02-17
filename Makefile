# Simplify build management

.PHONY: target env update build deploy lint test format

all: target

target:
	$(info ${HELP_MESSAGE})
	@exit 0

env:
	pipenv sync --dev

update:
	pipenv update --dev

dist:
	python setup.py sdist bdist_wheel

deploy: build
	twine upload --verbose dist/*

lint:
	#black --check awscfncli2/* tests/*
	pipenv run bandit -r awscfncli2 -c bandit
	pipenv run flake8 --format=pylint
	pipenv run pylint awscfncli2

test:
	pipenv run pytest tests/unit
	pipenv run pytest tests/unit

format:
	pipenv run black awscfncli2/* tests/*


define HELP_MESSAGE

env
  Boostrap enviroment.

update
  Update pipenv environment.

dist:
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
