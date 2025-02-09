# Build stage
FROM python:3.11.7-slim AS builder

WORKDIR /mem0-api

# Install build dependencies and poetry
RUN pip install --no-cache-dir poetry

# Configure poetry settings
RUN poetry config installer.max-workers 10 \
    && poetry config installer.parallel true \
    && poetry config virtualenvs.create false

# Copy only dependency files first
COPY pyproject.toml poetry.lock ./

# Add source with China mirrors
RUN poetry source add aliyun https://mirrors.aliyun.com/pypi/simple/
RUN poetry source add tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# Install dependencies with optimized settings
RUN poetry lock
RUN poetry install --only main --no-root --no-interaction --no-ansi \
    && rm -rf /root/.cache/pip/*

# Final stage
FROM python:3.11.7-slim

WORKDIR /mem0-api

# Copy only the necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . .

# Declare the port
EXPOSE ${MEM0_API_PORT}

# Run the application
CMD ["poetry", "run", "python", "app.py"]