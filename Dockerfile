FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y gcc libssl-dev && \
    apt-get clean

# Set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
