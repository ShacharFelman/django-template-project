# Dockerfile
FROM python:3.13-slim
LABEL maintainer="shaharfelmandev@gmail.com"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
# Update package list and install system dependencies (PostgreSQL client and bash)
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends postgresql-client bash && \
    # Create a Python virtual environment in /py
    python -m venv /py && \
    # Upgrade pip inside the virtual environment
    /py/bin/pip install --upgrade pip && \
    # Install Python dependencies from requirements.txt
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Clean up apt cache and temporary files to reduce image size
    rm -rf /var/lib/apt/lists/* /tmp/* && \
    # Create a non-root user for running the application
    useradd --create-home --shell /bin/bash django-user

ENV PATH="/scripts:/py/bin:$PATH"

USER django-user
