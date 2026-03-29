from redis import asyncio as aioredis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global redis client (initialized in main.py)
redis_client: aioredis.Redis = None

def get_redis_client() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL, 
            encoding="utf8", 
            decode_responses=True
        )
    return redis_client

async def is_token_blacklisted(token: str) -> bool:
    client = get_redis_client()
    try:
        return await client.exists(f"blacklist:{token}") > 0
    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}")
        return False

async def blacklist_token(token: str, expire_seconds: int):
    client = get_redis_client()
    try:
        await client.setex(f"blacklist:{token}", expire_seconds, "1")
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}")

async def set_otp(email: str, code: str, expire_seconds: int = 300):
    client = get_redis_client()
    try:
        await client.setex(f"otp:{email}", expire_seconds, code)
    except Exception as e:
        logger.error(f"Error setting OTP for {email}: {e}")

async def get_otp(email: str) -> str:
    client = get_redis_client()
    try:
        return await client.get(f"otp:{email}")
    except Exception as e:
        logger.error(f"Error retrieving OTP for {email}: {e}")
        return None

async def delete_otp(email: str):
    client = get_redis_client()
    try:
        await client.delete(f"otp:{email}")
    except Exception as e:
        logger.error(f"Error deleting OTP for {email}: {e}")

# Geo-spatial search helpers
async def geo_add_location(set_name: str, lng: float, lat: float, member_id: int):
    client = get_redis_client()
    try:
        await client.geoadd(set_name, (lng, lat, str(member_id)))
    except Exception as e:
        logger.error(f"Error adding geo location for {member_id} in {set_name}: {e}")

async def geo_remove_location(set_name: str, member_id: int):
    client = get_redis_client()
    try:
        await client.zrem(set_name, str(member_id))
    except Exception as e:
        logger.error(f"Error removing geo location for {member_id} from {set_name}: {e}")

async def geo_search_nearby(set_name: str, lng: float, lat: float, radius_km: float):
    """Returns a list of member_ids within the radius."""
    client = get_redis_client()
    try:
        results = await client.georadius(
            set_name, lng, lat, radius_km, unit="km",
            withdist=True, sort="ASC"
        )
        # Results look like [(b'member_id', distance), ...]
        return [{"id": int(res[0]), "dist": round(res[1], 2)} for res in results]
    except Exception as e:
        logger.error(f"Error searching nearby in {set_name}: {e}")
        return []
