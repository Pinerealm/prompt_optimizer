# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

RUN useradd -m appuser
USER appuser

# For local development
# CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]

# For production, use environment variable for port
CMD uvicorn main:app --port ${PORT:-8000} --host 0.0.0.0
