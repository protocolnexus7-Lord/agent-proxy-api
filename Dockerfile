# Use Microsoft's official Playwright Python image (pre-installed Linux browser deps)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose Render port
EXPOSE 10000

# Start Uvicorn app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
