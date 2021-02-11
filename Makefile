.PHONY: clean clean-statics clean-test clean-pyc clean-build help
.DEFAULT_GOAL := help

THIS_FILE := $(lastword $(MAKEFILE_LIST))

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-statics clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-statics:
	flask digest clean

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name 'vendor.*.js' -exec rm -f {} +
	find . -name '*.map' -exec rm -f {} +
	rm -f newswriter/static/js/app.js
	rm -f newswriter/static/js/runtime.js
	rm -f newswriter/templates/jsfiles.html
	rm -f newswriter/static/css/style.css
	rm -f newswriter/static/css/utils.css

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 newswriter tests

test: ## run tests quickly with the default Python
	python setup.py test

coverage: ## check code coverage quickly with the default Python
	python setup.py test --addopts --cov


dist: clean statics ## builds source and wheel package
	pip install --upgrade build
	python3 -m build
	ls -l dist

statics: ## Build statics
	cd jsclient && yarn run build && cd ..
	cd styles && yarn run build && cd ..
	flask digest compile

dev: ## setup development enviroment
	python -m pip install -e .
	@$(MAKE) -f $(THIS_FILE) clean
	@$(MAKE) -f $(THIS_FILE) statics
