"""
IntelliWealth – Redis Client
Provides async-compatible Redis connection for market and analytics caching.
"""

import json
import logging
from typing import Any, Optional

import redis

from app.config import get_settings

logger = logging.getLogger("intelliwealth.redis")
settings = get_settings()

# ---- Connection Pool ----
_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)


def get_redis() -> redis.Redis:
    """Return a Redis client from the connection pool."""
    return redis.Redis(connection_pool=_pool)


class CacheService:
    """
    Unified caching layer for market data and analytics results.
    All values are JSON-serialized for portability.
    """

    # ---- Key Prefixes ----
    MARKET_PREFIX = "market:"
    ANALYTICS_PREFIX = "analytics:"
    RISK_PREFIX = "risk:"
    SECTOR_PREFIX = "sector:"

    def __init__(self) -> None:
        self._redis = get_redis()

    # ---- Core Operations ----

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value. Returns None on miss or error."""
        try:
            raw = self._redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except (redis.RedisError, json.JSONDecodeError) as exc:
            logger.warning("Cache GET failed for key=%s: %s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value in cache with optional TTL (seconds)."""
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                self._redis.setex(key, ttl, serialized)
            else:
                self._redis.set(key, serialized)
            return True
        except (redis.RedisError, TypeError) as exc:
            logger.warning("Cache SET failed for key=%s: %s", key, exc)
            return False

    def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        try:
            self._redis.delete(key)
            return True
        except redis.RedisError as exc:
            logger.warning("Cache DELETE failed for key=%s: %s", key, exc)
            return False

    def flush_prefix(self, prefix: str) -> int:
        """Delete all keys matching a prefix. Returns count deleted."""
        try:
            keys = list(self._redis.scan_iter(match=f"{prefix}*", count=500))
            if keys:
                return self._redis.delete(*keys)
            return 0
        except redis.RedisError as exc:
            logger.warning("Cache FLUSH failed for prefix=%s: %s", prefix, exc)
            return 0

    # ---- Market Data Cache ----

    def get_market_data(self, asset_name: str) -> Optional[dict]:
        """Get cached market data for an asset."""
        return self.get(f"{self.MARKET_PREFIX}{asset_name}")

    def set_market_data(self, asset_name: str, data: dict) -> bool:
        """Cache market data for an asset."""
        return self.set(
            f"{self.MARKET_PREFIX}{asset_name}",
            data,
            ttl=settings.REDIS_CACHE_TTL,
        )

    # ---- Analytics Cache ----

    def get_analytics(self, cache_key: str) -> Optional[dict]:
        """Get cached analytics result."""
        return self.get(f"{self.ANALYTICS_PREFIX}{cache_key}")

    def set_analytics(self, cache_key: str, data: dict) -> bool:
        """Cache an analytics result."""
        return self.set(
            f"{self.ANALYTICS_PREFIX}{cache_key}",
            data,
            ttl=settings.REDIS_ANALYTICS_TTL,
        )

    # ---- Risk Cache ----

    def get_risk(self, portfolio_id: str) -> Optional[dict]:
        """Get cached risk metrics for a portfolio."""
        return self.get(f"{self.RISK_PREFIX}{portfolio_id}")

    def set_risk(self, portfolio_id: str, data: dict) -> bool:
        """Cache risk metrics for a portfolio."""
        return self.set(
            f"{self.RISK_PREFIX}{portfolio_id}",
            data,
            ttl=settings.REDIS_ANALYTICS_TTL,
        )

    def invalidate_risk(self, portfolio_id: str) -> bool:
        """Invalidate cached risk for a portfolio."""
        return self.delete(f"{self.RISK_PREFIX}{portfolio_id}")

    # ---- Health ----

    def ping(self) -> bool:
        """Check Redis connectivity."""
        try:
            return self._redis.ping()
        except redis.RedisError:
            return False
