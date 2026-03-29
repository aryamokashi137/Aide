# Aide - Comprehensive Student & Essential Services Platform

**Aide** (formerly EduCare Connect) is a modern, high-performance platform designed to bridge the gap between students, parents, and essential local services. It provides a unified ecosystem for education, accommodation, and medical support, enhanced by real-time location-based searching and intelligent caching.

This repository contains the **FastAPI-based Backend** that powers the **Aide Flutter Mobile Application**.

---

## 🛠️ Technical Stack

*   **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
*   **Database**: [PostgreSQL](https://www.postgresql.org/) (Relational Data Storage)
*   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) with [Alembic](https://alembic.sqlalchemy.org/) for migrations.
*   **In-Memory Database**: [Redis](https://redis.io/) (Used for Caching, Geo-Spatial Indexing, and Rate Limiting).
*   **Validation**: [Pydantic v2](https://docs.pydantic.dev/) for strict type safety and automatic Swagger documentation.
*   **Security**: [OAuth2 with JWT tokens](https://jwt.io/), Passlib (bcrypt) for secure password hashing.
*   **Real-time**: [WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) via Redis Pub/Sub.
*   **Task/Extensions**: [FastAPI-Limiter](https://github.com/long2ice/fastapi-limiter), [FastAPI-Cache](https://github.com/long2ice/fastapi-cache).

---

## 🚀 Key Features

### 🔍 1. Standardized API Filtering
- **Enum-Validated Parameters**: All categories (e.g., `specialization`, `meal_type`, `board`) use Python Enums for strict validation and interactive dropdowns in Swagger.
*   **Unified Filter Objects**: Modular `FilterParams` dependency classes for each entity (Schools, Hospitals, PGs, etc.).
*   **Dual-Path Access**: All search endpoints support both the root collection URL `/` and a dedicated `/filters` alias.

### 📍 2. Redis-Powered Geo-Spatial Intelligence
*   **High-Speed Proximity Search**: Leverages Redis Geo-spatial indexes (`GEOADD`, `GEORADIUS`) for millisecond-fast nearby searches.
*   **Smart Fallback**: Automatically falls back to database-level Haversine distance calculations if Redis is unavailable or coordinates are missing.
*   **Dynamic Radius**: Filter results within a user-defined radius (e.g., 5km, 20km).

### ⚡ 3. Intelligent Caching
*   **MD5 Search Caching**: Hashed cache keys derived from all filter parameters ensure repeat searches are served from Redis in milliseconds.
*   **Single-Entity Caching**: Individual detail endpoints (`GET /{id}`) utilize `@cache` decorators with smart expiration.

### 🏢 4. Comprehensive Service Modules
*   **Education Hub**: Colleges, Schools, Coaching Classes, and Mess Services.
*   **Medical Emergency**: Hospitals, Doctors, Ambulance Services, and Blood Banks.
*   **Stay & Accommodation**: PGs (Paying Guests) and Hostels with Amenity-based filtering.

### 🛡️ 5. Production Security
*   **Admin & Student Roles**: Role-based access control (RBAC) via modular FastAPI dependencies.
*   **Rate Limiting**: Protects authentication endpoints from abuse using Redis-based sliding windows.

---

## 📂 Project Structure

```text
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/          # Route handlers (Education, Medical, Stay, Auth)
│   │   └── api.py              # Main router inclusion hub
│   ├── core/                   # Core config, database, location, redis, and auth logic
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic validation schemas
│   └── services/               # Reusable business logic services
├── alembic/                    # Database migration versions and env scripts
├── scripts/                    # Utility scripts (init_db.py, sync_redis_geo.py)
├── .env.example                # Template for environment variables
└── README.md                   # You are here!
```

---

## 🏁 Getting Started

### 1. Prerequisites
*   Python 3.11+
*   PostgreSQL 14+
*   **Redis Server** (required for geo-spatial & caching)

### 2. Installation
```bash
# Navigate to backend 
cd backend

# Install dependencies
pip install -r requirements.txt
```

### 3. Database & Cache Initialization
```bash
# Apply migrations
alembic upgrade head

# Sync database records to Redis Geo-Index
python scripts/sync_redis_geo.py

# Initialize database (Admin user, etc.)
python scripts/init_db.py
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```
Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** to explore the API.

---

## 🛡️ License
This project is for educational and service-oriented purposes. All rights reserved.
