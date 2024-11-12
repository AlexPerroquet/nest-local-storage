FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry using the recommended method
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.6.1
ENV PATH="/opt/poetry/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
    && chmod a+x /opt/poetry/bin/poetry

# Set working directory
WORKDIR /workspace

# Copy poetry files
COPY pyproject.toml ./

# Configure poetry
ENV POETRY_VIRTUALENVS_CREATE=false

# Generate lock file and install dependencies
RUN poetry lock --no-update \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Create videos directory
RUN mkdir -p /workspace/videos

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]