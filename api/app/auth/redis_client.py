import redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.StrictRedis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True
)
