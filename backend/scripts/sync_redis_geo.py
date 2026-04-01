import sys
import os
import asyncio
from sqlalchemy.orm import Session

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.redis import get_redis_client, geo_add_location
from app.models.medical.hospital import Hospital
from app.models.medical.ambulance import Ambulance
from app.models.stay.pg import PG
from app.models.education.colleges import College
from app.models.education.schools import School
from app.models.education.coaching import Coaching
from app.models.education.mess import Mess

async def sync_all_geo():
    db = SessionLocal()
    redis = get_redis_client()
    
    entities = [
        (Hospital, "geo:hospitals"),
        (Ambulance, "geo:ambulances"),
        (PG, "geo:pgs"),
        (College, "geo:colleges"),
        (School, "geo:schools"),
        (Coaching, "geo:coaching"),
        (Mess, "geo:mess"),
    ]
    
    print(" Starting Geo-spatial data sync from PostgreSQL to Redis...")
    
    try:
        for model, redis_key in entities:
            print(f"Syncing {model.__name__}...")
            
            # Clear existing index for this entity
            await redis.delete(redis_key)
            
            # Fetch all active records with lat/lon
            records = db.query(model).filter(
                model.is_active == True,
                model.latitude.isnot(None),
                model.longitude.isnot(None)
            ).all()
            
            total = 0
            for record in records:
                try:
                    # Redis geoadd (lon, lat, member_id)
                    await redis.geoadd(redis_key, (record.longitude, record.latitude, str(record.id)))
                    total += 1
                except Exception as e:
                    print(f"Skipping {model.__name__} {record.id} due to invalid coords: {e}")
            
            print(f"✅ Successfully synced {total} {model.__name__} records to '{redis_key}'.")
            
        print("\n✨ ALL Geo-spatial data synced successfully!")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(sync_all_geo())
