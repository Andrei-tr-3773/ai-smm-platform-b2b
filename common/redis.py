import hashlib
import json
import os

import redis
from redis.client import Redis


_redis_client = None


def get_redis_client():
    if _redis_client is None:
        print("Redis module is not initialized. Running init now...")
        return module_init()
    return _redis_client


def redis_safe_ping(rc: Redis) -> bool:
    if rc is None:
        raise ValueError(
            "Redis client is None. Initialize `common.redis` " "via `common.redis.module_init()` function."
        )
    try:
        return rc.ping()
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"Redis ping error: {e}")
        return False


def get_hash_key(prefix, *args, **kwargs) -> str:
    _pre_hash_key = json.dumps((args, kwargs))
    print(f"Pre-hash key: {prefix}:{_pre_hash_key[:100]}...")
    sha256 = hashlib.sha256()
    sha256.update(_pre_hash_key.encode("utf-8"))
    _key = f"{prefix}:" f"{sha256.hexdigest()}"
    print(f"Hashed key: {_key}")
    return _key


def module_init():
    global _redis_client
    DEFAULT_REDIS_HOST = "localhost"
    DEFAULT_SOCKET_TIMEOUT_SECONDS = 10
    try:
        redis_host = os.getenv("REDIS_HOST", DEFAULT_REDIS_HOST)
        redis_port = int(os.getenv("REDIS_PORT_OVERRIDE", "6379"))
        print(f"Trying to connect to Redis at {redis_host}:{redis_port}")
        _redis_client = Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            socket_timeout=DEFAULT_SOCKET_TIMEOUT_SECONDS,
        )
        _redis_client.ping()
        print("Connected to Redis. Setting up LLM cache...")
        return _redis_client
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"Cannot connect to Redis: {e}. Skipping LLM cache...")
