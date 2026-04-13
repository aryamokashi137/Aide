from fastapi import FastAPI
import logging
from app.api.v1.api import api_router
from app.core.database import Base, engine

logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="aide API",
    version="1.0.0"
)

# Ensure static directory exists
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

from app.core.config import settings

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://localhost:5001",
        "http://localhost:5002",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5002",
    ],
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
        
        from app.core.redis import get_redis_client
        redis_c = get_redis_client()
        FastAPICache.init(RedisBackend(redis_c), prefix="fastapi-cache")
        logger.info("Redis cache initialized successfully")
        
        # Initialize Rate Limiter
        from fastapi_limiter import FastAPILimiter
        await FastAPILimiter.init(redis_c)
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

