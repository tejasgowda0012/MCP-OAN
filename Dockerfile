FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY python/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY python/ .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/log/supervisor

ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=3001 \
    MCP_TRANSPORT=streamable-http \
    ADMIN_PORT=3002 \
    ADMIN_USERNAME=admin \
    ADMIN_PASSWORD=changeme

EXPOSE 3001 3002

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]