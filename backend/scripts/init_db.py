#!/usr/bin/env python3
"""
Initialize database with default admin user
Run this AFTER migrations (alembic upgrade head)
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


ADMIN_EMAIL = "admin@educareconnect.com"
ADMIN_PASSWORD = "admin123"  # ⚠ CHANGE IN REAL PRODUCTION
ADMIN_FULL_NAME = "Super Admin"


def init_db():
    """Create default admin user if not exists"""
    db: Session = SessionLocal()

    try:
        #  Check if users table exists
        try:
            db.execute(text("SELECT 1 FROM users LIMIT 1"))
        except Exception:
            print(" Database tables don't exist yet!")
            print("\nRun migrations first:")
            print("   alembic upgrade head\n")
            return

        #  Check if admin already exists
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

        if admin:
            print(" Admin user already exists")
            print(f"   Email: {admin.email}")
            return

        # Create admin user
        new_admin = User(
            full_name=ADMIN_FULL_NAME,
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        print("Default admin created successfully!")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print("\n⚠ IMPORTANT: Change this password in production!")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    init_db()