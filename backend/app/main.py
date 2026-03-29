from fastapi import FastAPI
import logging
from app.api.v1.api import api_router
from app.core.database import Base, engine

logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="aide API",
    version="1.0.0"
)

from app.core.config import settings

# Enable CORS using whitelist from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def on_startup():
    # Initialize Redis for caching
    try:
        from redis import asyncio as aioredis
        from fastapi_cache import FastAPICache
        from fastapi_cache.backends.redis import RedisBackend
        
        redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        logger.info("Redis cache initialized successfully")
        # Initialize Rate Limiter
        from fastapi_limiter import FastAPILimiter
        import redis.asyncio as aioredis
        
        limiter_redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(limiter_redis)
        logger.info("FastAPI Limiter initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize Redis services: {e}")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning("Could not create database tables on startup: %s", e)


# Include API v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Aide Backend Running"}


from fastapi import WebSocket, WebSocketDisconnect
import asyncio

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    
    from app.core.redis import get_redis_client
    redis = get_redis_client()
    pubsub = redis.pubsub()
    
    # Subscribe to a channel specific to this user
    channel_name = f"user_notifications:{user_id}"
    await pubsub.subscribe(channel_name)
    
    logger.info(f"User {user_id} connected to WebSocket and subscribed to {channel_name}")
    
    try:
        while True:
            # Check for new messages in Redis with a small timeout
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = message["data"]
                await websocket.send_text(f"Notification: {data}")
            
            # Keep-alive or handle client messages if needed
            # await websocket.receive_text() # This would block, so be careful
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from WebSocket")
        await pubsub.unsubscribe(channel_name)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await pubsub.unsubscribe(channel_name)

