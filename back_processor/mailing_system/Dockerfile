# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /app/venv
# Make sure we use the virtualenv:
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime system dependencies (libpq is needed for psycopg)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Change ownership of the application directory to the non-root user
# This allows the app to write to local directories if needed (e.g., for temporary files or FAISS index if not volume mounted)
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/ || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
