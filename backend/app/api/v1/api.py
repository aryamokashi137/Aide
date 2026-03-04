from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints.education import colleges


api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

api_router.include_router(
    colleges.router,
    prefix="/education/colleges",
    tags=["Colleges"]
)