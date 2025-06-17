.PHONY: install update clean env build deploy

# Default Python interpreter
PYTHON := python
UV := uv

# Install production dependencies
install:
	$(UV) pip install -r requirements.txt

# Update dependencies to their latest compatible versions
update:
	$(UV) pip compile pyproject.toml --upgrade -o requirements.txt

# Clean up Python cache files and build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} + 

# activate env created via uv venv bookcellent --python 3.13
env:
	source ./bookcellent/bin/activate

# build
build:
	${PYTHON} main.py

# deploy changes to github
deploy: build
	@if ! command -v ollama >/dev/null 2>&1; then \
		echo "Error: ollama is not installed. Please install it first."; \
		exit 1; \
	fi
	@if ! git diff --quiet; then \
		COMMIT_MSG=$$(./generate_commit_msg.sh) && \
		if [ $$? -eq 0 ]; then \
			echo "$${COMMIT_MSG}" && \
			git commit -am "$${COMMIT_MSG}" && \
			git push origin master && \
			sleep 3 && \
			gh run watch; \
		else \
			echo "Failed to generate commit message"; \
			exit 1; \
		fi \
	else \
		echo "No changes to commit"; \
		exit 0; \
	fi
