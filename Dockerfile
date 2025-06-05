# Use Python 3.12.7 base image
FROM python:3.12.7-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy all files to container
COPY . .

# Install dependencies with uv
RUN uv pip install --system -r requirements.txt

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
