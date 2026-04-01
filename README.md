# Aide - Comprehensive Student & Essential Services Platform

**Aide** (formerly EduCare Connect) is a modern, high-performance platform designed to bridge the gap between students, parents, and essential local services. It provides a unified ecosystem for education, accommodation, and medical support, enhanced by real-time location-based searching and intelligent caching.

This repository contains the **FastAPI-powered Backend** and the **Flutter-based Cross-Platform Application**.

---

## 🛠️ Technology Stack

### Backend
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
*   **Database**: [PostgreSQL](https://www.postgresql.org/) (Relational Storage)
*   **Caching & Geo-Spatial**: [Redis](https://redis.io/) (GEOADD, MD5 Query Caching)
*   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/)

### Frontend (Flutter)
*   **Framework**: [Flutter SDK](https://flutter.dev/) (Cross-platform)
*   **State Management**: [Provider](https://pub.dev/packages/provider)
*   **Geolocation**: [Geolocator](https://pub.dev/packages/geolocator)
*   **Networking**: [http](https://pub.dev/packages/http)
*   **Styling**: Premium Dark Mode with Outlined Iconography

---

## 🚀 Key Features

### 🔍 1. Smart Education Hub
- **Tabbed Navigation**: Schools, Colleges, Coaching Centers, and Mess services. (Dynamic)
- **Nearby Sorting**: Automated "Nearby on Top" logic based on real-time student coordinates.

### 📍 2. Redis Geo-Spatial Indexing
- **Micro-second Proximity Search**: Uses Redis `GEO` commands for ultra-fast location filtering.
- **Inclusive Search**: Results are visible worldwide, with distant results labeled in-UI.

### 🌓 3. Modern Premium UI
- **Global Dark Mode**: Full system-aware theme compatibility.
- **Micro-animations**: Smooth transitions between service tabs and detail pages.

---

## 🏁 Getting Started

### 1. Backend Setup
```bash
# Navigate to backend 
cd backend

# Install dependencies and activate venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and seed data
alembic upgrade head
python seed_data.py

# Launch server
uvicorn app.main:app --reload --port 8000
```
Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** to explore the API.

### 2. Frontend Setup (Flutter)
```bash
# Navigate to frontend
cd Educare_connect/frontend/educonnect

# Install dependencies
flutter pub get

# Launch for Web (Premium Experience)
flutter run -d chrome --web-port 2001
```

---

## 📂 Project Structure
```text
├── backend/                # FastAPI logic, Postgres Models, Redis Caching
├── frontend/educare/       # Flutter application, UI Components, API Services
├── how_to_run.txt          # Quick setup guide for developers
└── README.md               # Overview of the project architecture
```

---

## 🛡️ License
This project is for educational and service-oriented purposes. All rights reserved.
