from app.core.database import SessionLocal
from app.models.education.schools import School, SchoolType, BoardType
from app.models.education.coaching import Coaching, CoachingType
from app.models.education.mess import Mess, MessType
from app.models.stay.pg import PG, GenderType, RoomType
from app.core.redis import geo_add_location
import asyncio

async def seed():
    db = SessionLocal()

    # Sample School
    if db.query(School).count() == 0:
        school1 = School(
            name="Saint Xavier High School",
            type=SchoolType.HIGHER_SECONDARY,
            board=BoardType.CBSE,
            address="Camp, Pune, Maharashtra",
            latitude=18.5204,
            longitude=73.8567,
            fees="45,000",
            is_active=True,
            phone_number="+91 1111111111"
        )
        db.add(school1)
        print("Seeded School")

    # Sample Coaching
    if db.query(Coaching).count() == 0:
        coaching1 = Coaching(
            name="IIT Academy Coaching",
            coaching_type=CoachingType.OFFLINE,
            address="Deccan Gymkhana, Pune",
            latitude=18.5160,
            longitude=73.8400,
            fees="85,000",
            is_active=True,
            phone_number="+91 2222222222"
        )
        db.add(coaching1)
        print("Seeded Coaching")

    # Sample Mess
    if db.query(Mess).count() == 0:
        mess1 = Mess(
            name="Student Delight Mess",
            meal_types=MessType.BOTH,
            address="Viman Nagar, Pune",
            latitude=18.5679,
            longitude=73.9143,
            monthly_charges="3,200",
            is_active=True,
            phone_number="+91 3333333333"
        )
        db.add(mess1)
        print("Seeded Mess")

    # Sample PG
    if db.query(PG).count() == 0:
        pg1 = PG(
            name="Emerald Boys Guest House",
            gender=GenderType.BOYS,
            room_type=RoomType.DOUBLE,
            address="Baner Road, Near Pancard Club",
            latitude=18.5590,
            longitude=73.7900,
            one_month_rent=8500,
            is_active=True,
            facilities_available="WiFi, AC, Laundry, 3 Meals",
            phone_number="+91 4444444444"
        )
        db.add(pg1)
        print("Seeded PG")

    db.commit()

    # Sync to Redis Geo
    for s in db.query(School).all():
        await geo_add_location("geo:schools", s.longitude, s.latitude, s.id)
    for c in db.query(Coaching).all():
        await geo_add_location("geo:coaching", c.longitude, c.latitude, c.id)
    for m in db.query(Mess).all():
        await geo_add_location("geo:mess", m.longitude, m.latitude, m.id)
    for p in db.query(PG).all():
        await geo_add_location("geo:pgs", p.longitude, p.latitude, p.id)

    db.close()
    print("Seed complete and synced to Redis!")

if __name__ == "__main__":
    asyncio.run(seed())
