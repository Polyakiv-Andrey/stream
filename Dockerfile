FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y gcc libssl-dev && \
    apt-get clean

# Set work directory
WORKDIR /app

# Ensure the working directory exists and is writable
RUN mkdir -p /app && chmod -R 755 /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-w", "4", "-k", "eventlet", "-b", "0.0.0.0:5000", "app:app"]
