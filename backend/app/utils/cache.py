"""Caching utilities using Redis."""

import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from redis import asyncio as aioredis

from app.core.config import settings


class CacheService:
    """Redis cache service."""

    def __init__(self):
        """Initialize cache service."""
        self.redis: Optional[aioredis.Redis] = None
        self._default_ttl = 3600  # 1 hour

    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                str(settings.redis_url),
                encoding="utf-8",
                decode_responses=True
            )

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis:
            await self.connect()

        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful
        """
        if not self.redis:
            await self.connect()

        ttl = ttl or self._default_ttl

        try:
            serialized_value = json.dumps(value)
        except (TypeError, ValueError):
            serialized_value = str(value)

        return await self.redis.setex(key, ttl, serialized_value)

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        if not self.redis:
            await self.connect()

        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        if not self.redis:
            await self.connect()

        return await self.redis.exists(key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            await self.connect()

        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.

        Args:
            prefix: Key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Generated cache key
        """
        # Create a deterministic key from arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_hash = hashlib.md5(
            json.dumps(key_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        return f"{prefix}:{key_hash}"


# Global cache instance
cache = CacheService()


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds

    Usage:
        @cached(prefix="market_analysis", ttl=7200)
        async def analyze_market(product: str, region: str):
            # expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache.cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator to invalidate cache on function execution.

    Args:
        pattern: Cache key pattern to invalidate

    Usage:
        @invalidate_cache("market_analysis:*")
        async def update_market_data(data):
            # update operation
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)

            # Invalidate cache
            await cache.clear_pattern(pattern)

            return result

        return wrapper
    return decorator
