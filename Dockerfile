# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Expose the application port
EXPOSE 8000

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Rust and its dependencies
RUN apt-get update && apt-get install -y curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    rm -rf /var/lib/apt/lists/*

# Set the PATH for Rust
ENV PATH="/root/.cargo/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Create a non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

