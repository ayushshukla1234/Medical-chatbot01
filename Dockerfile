FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (optional but useful for sentence-transformers)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port your app uses
EXPOSE 5001

# Run your app
CMD ["python", "app.py"]
