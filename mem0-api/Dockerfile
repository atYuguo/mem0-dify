# Build stage
FROM python:3.11.7-slim

WORKDIR /mem0-api

# Install build dependencies and poetry
RUN pip install --no-cache-dir poetry

# Configure poetry settings
RUN poetry config installer.max-workers 10 \
    && poetry config installer.parallel true \
    && poetry config virtualenvs.create false

# Copy only dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies with optimized settings
RUN poetry lock
RUN poetry install --only main --no-root --no-interaction --no-ansi \
    && rm -rf /root/.cache/pip/*

# Copy application code
COPY . .

# Declare the port
EXPOSE ${MEM0_API_PORT}

# Run the application
CMD ["poetry", "run", "uvicorn", "app:app"]
