FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY python/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY python/ .

ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=3001 \
    MCP_TRANSPORT=streamable-http

EXPOSE 3001

CMD ["python", "server.py"]