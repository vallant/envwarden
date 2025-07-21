# Makefile for envwarden-py

.PHONY: install test demo clean help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install envwarden-py in development mode
	pip install -e .

test:  ## Run all tests
	python -m unittest discover tests/ -v

demo:  ## Run the demo script showing output formats
	python demo.py

clean:  ## Clean up build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

build:  ## Build the package
	python setup.py sdist bdist_wheel

lint:  ## Run linting (if flake8 is available)
	@which flake8 > /dev/null && flake8 envwarden_py/ tests/ || echo "flake8 not available"

format:  ## Format code (if black is available)
	@which black > /dev/null && black envwarden_py/ tests/ || echo "black not available"