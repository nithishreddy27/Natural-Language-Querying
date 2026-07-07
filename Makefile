# Makefile for NLP Query Understanding System

.PHONY: install test demo clean lint format docker-build docker-run

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest black flake8 mypy jupyter

# Testing
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=src --cov-report=html

# Demo and examples
demo:
	python examples/demo.py

interactive-demo:
	python -c "from examples.demo import interactive_demo; interactive_demo()"

# Code quality
lint:
	flake8 src/ tests/ examples/
	mypy src/

format:
	black src/ tests/ examples/ data/

format-check:
	black --check src/ tests/ examples/ data/

# Docker
docker-build:
	docker build -t nlp-query-system .

docker-run:
	docker run -it --rm -p 8000:8000 nlp-query-system

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

# Performance testing
performance-test:
	python -c "from tests.test_system import run_performance_test; run_performance_test()"

# Model management
download-models:
	python -c "from src.query_understanding import QueryUnderstandingSystem; system = QueryUnderstandingSystem()"

# Documentation
docs:
	python -c "import pydoc; pydoc.writedoc('src.query_understanding')"
	python -c "import pydoc; pydoc.writedoc('src.intent_classifier')"
	python -c "import pydoc; pydoc.writedoc('src.vector_store')"

# All-in-one setup
setup: install download-models test demo
	@echo "✅ Setup completed successfully!"

# Development workflow
dev-setup: install-dev format lint test
	@echo "🚀 Development environment ready!"
