.PHONY: help install run run-help clean test lint format

help:
	@echo "Available commands:"
	@echo "  make install         Sync dependencies using uv"
	@echo "  make run             Run the tutorial flow (requires --repo or --dir argument)"
	@echo "  make run-help        Show help for available run arguments"
	@echo "  make test            Run tests (if available)"
	@echo "  make lint            Run linting checks"
	@echo "  make format          Format Python code"
	@echo "  make clean           Remove generated files and cache"

install:
	uv sync
	uv pip install -r requirements.txt

run:
	uv run python main.py $(ARGS)

run-help:
	uv run python main.py --help

test:
	@echo "No tests configured yet. Add pytest or similar testing framework."

lint:
	@echo "Running Python linting..."
	uv run pylint --disable=all --enable=E,F nodes.py flow.py main.py utils/ 2>/dev/null || echo "Note: Install pylint for full linting support"

format:
	@echo "Formatting Python files..."
	uv run black --line-length 100 main.py flow.py nodes.py utils/ 2>/dev/null || echo "Note: Install black for automatic formatting support"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '.DS_Store' -delete 2>/dev/null || true
	rm -rf build/ dist/ .eggs/ *.egg-info/ 2>/dev/null || true
	@echo "Clean complete"

.PHONY: analyze
analyze:
	uv run python main.py --dir  tmp/kagent        --include "*.go" "*.py" "*.js" --exclude "tests/*" --max-size 50000
	uv run python main.py --dir  tmp/kagent-tools  --include "*.go" "*.py" "*.js" --exclude "tests/*" --max-size 50000

