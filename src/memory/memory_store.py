import redis.asyncio as redis
from observability.logger import logger, log_error
from config import config

async def build_redis_client() -> redis.Redis | None:
    """
    Initializes and returns an asynchronous Redis client based on environment variables.
    """
    
    if not config.REDIS_HOST:
        logger.warning("REDIS_HOST not provided. Running without Redis session management.")
        return None

    try:
        client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            username=config.REDIS_USERNAME,
            password=config.REDIS_PASSWORD,
            ssl=config.REDIS_SSL,
            decode_responses=True # Ensure responses are strings, not bytes
        )
        
        # Test connection
        await client.ping()
        logger.info(f"Successfully connected to Redis Cloud at {config.REDIS_HOST}:{config.REDIS_PORT}")
        return client
        
    except Exception as e:
        log_error(e, "Redis Cloud Connection")
        return None
