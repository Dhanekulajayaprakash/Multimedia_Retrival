import os
from celery import Celery

# Check if we should run in eager (synchronous) mode for testing/local development.
# If redis is not running, we automatically default to eager mode so the app still runs.
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_available = False
try:
    import redis
    r = redis.Redis.from_url(redis_url, socket_connect_timeout=1)
    r.ping()
    redis_available = True
except Exception:
    pass

always_eager = os.getenv("CELERY_ALWAYS_EAGER", "False").lower() in ("true", "1", "yes")
if not redis_available:
    print("⚠️ Redis is not running. Falling back to Celery Eager Mode (tasks run synchronously).")
    always_eager = True

app = Celery(
    "worker",
    broker=redis_url if redis_available else "memory://",
    backend=redis_url if redis_available else "cache+memory://",
    include=[
        "workers.image",
        "workers.audio",
        "workers.video",
        "workers.document"
    ]
)

app.conf.update(
    task_always_eager=always_eager,
    task_eager_propagates=always_eager
)

