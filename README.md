# EduCare Connect Backend

EduCare Connect is a comprehensive platform designed to bridge the gap between students, parents, and essential services like education, accommodation, and medical support.

This repository contains the **FastAPI-based Backend** for the EduCare Connect mobile application (built with Flutter).

## 🚀 Features

### 👤 User & Profile Management
- **Authentication**: JWT-based secure login and registration with Role-Based Access Control (RBAC).
- **Comprehensive Profiles**: Management of user details including emergency contacts, blood group, social handles, and profile images.

### 🎓 Education Module
- **Colleges, Schools, & Coaching**: Extensive database of educational institutions.
- **Mess Services**: Directory of meal providers for students.
- **Location-Based Search**: Find institutions and services nearby using real-time distance calculation.

### 🏠 Stay Module (Accommodation)
- **Hostels & PGs**: Detailed listings for student accommodation with filters for gender, rent, deposit, and AC availability.
- **Nearby Search**: Quick access to stays closest to the user's current location.

### 🏥 Medical Module
- **Hospitals, Doctors, & Blood Banks**: Essential medical directory for emergencies.
- **Ambulances**: Quick contact and location data for ambulance providers.

### ⭐ Engagement
- **Review System**: Users can rate and review institutions and stays.
- **Soft Deletion**: All data is managed with an `is_active` flag to ensure data integrity and easy recovery.

---

## 🛠️ Technology Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: **PostgreSQL** (Used for both local development and production)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Frontend**: Flutter (Mobile Application)

---

## 🏃 How to Run

### 1. Prerequisites
- Python 3.11+
- **PostgreSQL** installed and running
- Virtual Environment (recommended)

### 2. Setup
```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/educare_connect
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the Server
```powershell
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. You can access the interactive documentation at `http://localhost:8000/docs`.

### 5. Database Migrations
Whenever you update models:
```powershell
# Generate migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

---

## 📍 Nearby Search Implementation
The backend uses the **Haversine Formula** to calculate distances in kilometers. 
Example query parameters for nearby search:
- `lat`: User's current latitude
- `lon`: User's current longitude
- `radius`: Search radius in kilometers (e.g., `5.0`)
- `name`: Filter by name/provider

---

## 📝 Current Scope Note
- **Database**: Exclusively using **PostgreSQL**. No SQLite support is included.
- **Notifications & SMTP**: Currently disabled (no active email provider/SMTP).
- **ML Integration**: Currently postponed for future scope.
- **Frontend**: The mobile application is built using **Flutter**.
