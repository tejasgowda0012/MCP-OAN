"""Cache — Redis or in-memory (USE_MEMORY_CACHE=true for local dev)."""
import os
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from vistaar_mcp.app.config import settings
from vistaar_mcp.helpers.utils import get_logger

logger = get_logger(__name__)

_use_memory = os.getenv("USE_MEMORY_CACHE", "").strip().lower() in ("1", "true", "yes", "on")

if _use_memory:
    cache = Cache(Cache.MEMORY, serializer=JsonSerializer(), ttl=settings.default_cache_ttl)
    logger.info("Cache configured with in-memory backend (USE_MEMORY_CACHE=true)")
else:
    cache = Cache(
        Cache.REDIS,
        endpoint=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        serializer=JsonSerializer(),
        ttl=settings.default_cache_ttl,
        timeout=settings.redis_socket_timeout,
        pool_max_size=settings.redis_max_connections,
        key_builder=lambda key, namespace: (
            f"{settings.redis_key_prefix}{namespace}:{key}"
            if namespace
            else f"{settings.redis_key_prefix}{key}"
        ),
    )
    logger.info(
        f"Cache configured with Redis at {settings.redis_host}:{settings.redis_port}"
    ) 