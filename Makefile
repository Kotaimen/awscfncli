# Simplify build management

env:
	pipenv sync --dev

test:
	pytest --cov awscfncli2 tests/unit

dev: lint test

lint:
	flake8 --format=pylint
	bandit -r awscfncli2 -c bandit

black:
	black awscfncli2/* tests/*

black-check:
	black --check awscfncli2/* tests/*
