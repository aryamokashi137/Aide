from fastapi import FastAPI
import logging
from app.api.v1.api import api_router
from app.core.database import Base, engine

logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EduCare Connect API",
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
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning("Could not create database tables on startup: %s", e)


# Include API v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "EduCare Connect Backend Running"}

