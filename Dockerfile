FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -sSf https://install.python-poetry.org | python3 - && \
  curl -sSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc && \
  . ~/.bashrc

# Set working directory
WORKDIR /app

# Copy requirements or define them here
COPY . .

# Install packages directly without virtual environment
RUN pip install -U agno yfinance packaging openai fastapi uvicorn ollama

# Set environment variables
ENV PYTHONPATH=/app
# OPENAI_API_KEY is provided via .env (docker-compose env_file)
# Default command
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--reload"]