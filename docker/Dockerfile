FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVICE_TYPE=web

# Update and install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Install Python dependencies
COPY ..requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY ../src /src

# Copy and set permissions for the startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8000

# Use the startup script as the entry point
CMD ["/start.sh"]