# Stage 1: Build Stage
FROM python:3.9-slim as builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages in a virtual environment
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.9-slim

# Copy the virtual environment from the builder stage
COPY --from=builder /venv /venv

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Expose the port on which the FastAPI app will run
EXPOSE 8000

# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
