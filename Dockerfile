FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create data directory with proper permissions
RUN mkdir -p data && chmod 777 data

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 5000
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
