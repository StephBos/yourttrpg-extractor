FROM python:3.11-slim

WORKDIR /app

# Ensure Python output is unbuffered so logs stream immediately
ENV PYTHONUNBUFFERED=1

# Install system dependencies for pytesseract and other packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

#Expose the port for the API
EXPOSE 8000/tcp

# Run the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
