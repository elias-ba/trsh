.PHONY: help test format lint clean install

help:
	@echo "trsh - Makefile commands:"
	@echo "  make test       - Run tests"
	@echo "  make format     - Format code with black"
	@echo "  make lint       - Run pylint"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make install    - Install trsh"

test:
	pytest test_trsh.py -v

test-cov:
	pytest --cov=trsh --cov-report=html test_trsh.py

format:
	black trsh.py test_trsh.py

lint:
	pylint trsh.py

type-check:
	mypy trsh.py

clean:
	rm -rf __pycache__/ .pytest_cache/ htmlcov/ .coverage
	find . -name "*.pyc" -delete

install:
	pip install -e .

check-all: format lint test
	@echo "✓ All checks passed!"