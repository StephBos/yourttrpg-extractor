FROM python:3.11-slim

WORKDIR /app

# Ensure Python output is unbuffered so logs stream immediately
ENV PYTHONUNBUFFERED=1

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

#Expose the port for the API
EXPOSE 8000/tcp

# Run the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
