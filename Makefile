-include .env

.PHONY: help run shell migrations migrate test lint format clean

help: ## Display this help screen
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 4) } ' $(MAKEFILE_LIST)

## Development
run: ## Start the local Django development server
	uv run python3 manage.py runserver

shell: ## Open the Django shell
	uv run python3 manage.py shell

migrations: ## Generate new database migrations
	uv run python3 manage.py makemigrations

migrate: ## Apply database migrations
	uv run python3 manage.py migrate

## Code Quality & Testing
test: ## Run the Django test suite using pytest
	uv run python3 manage.py test --settings=sales_email_scribe.settings_test

lint: ## Run ruff checks
	uv run ruff check .

lint-fix: ## Run ruff checks and apply any fixes where appropriate
	uv run ruff check --fix .

format: ## Format code using ruff
	uv run ruff format .

## Utility
clean: ## Remove temporary python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
