import sentry_sdk
import os
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

# Initialize Sentry (optional)
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development")
    )
    logger.info("✓ Sentry monitoring enabled")
else:
    logger.warning("⚠ Sentry DSN not configured - error tracking disabled")

# Metrics storage
_metrics = []

class Metric:
    def __init__(self, name: str, value: float, tags: dict = None):
        self.name = name
        self.value = value
        self.tags = tags or {}
        self.timestamp = time.time()

def track_metric(name: str, value: float, tags: dict = None):
    """Track a metric"""
    metric = Metric(name, value, tags)
    _metrics.append(metric)
    logger.info(f"📊 Metric: {name}={value} {tags or ''}")

def track_execution_time(metric_name: str):
    """Decorator to track execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                track_metric(metric_name, duration, {"status": "success"})
                return result
            except Exception as e:
                duration = time.time() - start
                track_metric(metric_name, duration, {"status": "error"})
                logger.error(f"❌ {metric_name} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator

def get_metrics():
    """Get all metrics"""
    return _metrics

def clear_metrics():
    """Clear metrics (for testing)"""
    global _metrics
    _metrics = []
