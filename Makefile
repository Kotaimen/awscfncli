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

build:
	python setup.py sdist bdist_wheel

deploy: build
	twine upload --verbose dist/*

lint:
	black --check awscfncli2/* tests/*
	bandit -r awscfncli2 -c bandit
	flake8 --format=pylint
	pylint awscfncli2

test:
	pytests

format:
	black awscfncli2/* tests/*


define HELP_MESSAGE

env
  Boostrap enviroment.

update
  Update pipenv environment.

build:

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
