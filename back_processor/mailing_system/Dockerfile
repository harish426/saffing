# Stage 1: Builder
# To rebuild and push the base image:
#   docker build -f Dockerfile.base -t harish426/staffing-backend-base:latest .
#   docker push harish426/staffing-backend-base:latest
FROM harish426/staffing-backend-base:latest as builder

WORKDIR /app

# Virtual environment is already set up in the base image
ENV PATH="/app/venv/bin:$PATH"

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
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
