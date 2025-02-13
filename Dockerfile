FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set up working directory
WORKDIR /app

# Copy all application code
COPY . .

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Install Playwright and browsers
RUN poetry run playwright install --with-deps chromium

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "8000"]