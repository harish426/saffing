# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for psycopg or others)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (using 8001 as per your code)
EXPOSE 8001

# Command to run the application
# Using 0.0.0.0 to allow external access within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
