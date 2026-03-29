from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints.education import colleges
from app.api.v1.endpoints.education import schools
from app.api.v1.endpoints.education import coaching
from app.api.v1.endpoints.education import mess
from app.api.v1.endpoints.stay import hostels
from app.api.v1.endpoints.stay import pg
from app.api.v1.endpoints.profile import profile
from app.api.v1.endpoints import user
from app.api.v1.endpoints import settings
from app.api.v1.endpoints import notification
from app.api.v1.endpoints.medical import hospitals, doctors, blood_banks, ambulances



api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

api_router.include_router(
    colleges.router,
    prefix="/education"
)

api_router.include_router(
    schools.router,
    prefix="/education"
)

api_router.include_router(
    coaching.router,
    prefix="/education"
)

api_router.include_router(
    mess.router,
    prefix="/education"
)

api_router.include_router(
    hostels.router,
    prefix="/stay"
)

api_router.include_router(
    pg.router,
    prefix="/stay"
)

api_router.include_router(
    profile.router,
    prefix="/profile"
)

api_router.include_router(
    user.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    settings.router
)

api_router.include_router(
    notification.router
)

# Medical Group
api_router.include_router(hospitals.router, prefix="/medical")
api_router.include_router(doctors.router, prefix="/medical")
api_router.include_router(blood_banks.router, prefix="/medical")
api_router.include_router(ambulances.router, prefix="/medical")
