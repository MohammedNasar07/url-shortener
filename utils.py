# utils.py
import os
import redis
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
)


def get_redis():
    """Get Redis client with connection check"""
    try:
        redis_client.ping()
        return redis_client
    except (redis.ConnectionError, redis.TimeoutError):
        # Redis is down, return None for graceful degradation
        return None


# Base62 encoding alphabet
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)


def encode_base62(num: int) -> str:
    """Convert integer to base62 string"""
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        result.append(ALPHABET[remainder])
    return "".join(reversed(result))


def validate_code(code: str) -> bool:
    """Validate short code format"""
    if not (1 <= len(code) <= 16):
        return False
    return all(c in ALPHABET for c in code)


class CacheStats:
    """Track cache performance metrics"""

    hits = 0
    misses = 0

    @classmethod
    def record_hit(cls):
        cls.hits += 1

    @classmethod
    def record_miss(cls):
        cls.misses += 1

    @classmethod
    def report(cls):
        total = cls.hits + cls.misses
        hit_rate = (cls.hits / total * 100) if total > 0 else 0
        return {
            "cache_hits": cls.hits,
            "cache_misses": cls.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total,
        }

    @classmethod
    def reset(cls):
        """Reset stats (useful for testing)"""
        cls.hits = 0
        cls.misses = 0
