"""
IntelliWealth – Portfolio Service Database Seeding
Populates initial data after migrations.
"""

from app.database import SessionLocal
from app.models.customer import Customer
from app.auth.jwt_handler import hash_password
import uuid


def seed_admin_user():
    """Seed default admin user if not exists."""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing = db.query(Customer).filter(Customer.email == "admin@intelliwealth.io").first()
        if existing:
            print("[seed] Admin user already exists, skipping.")
            return

        # Create admin user
        admin = Customer(
            id=uuid.uuid4(),
            name="Platform Admin",
            email="admin@intelliwealth.io",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("[seed] ✓ Admin user created successfully")
    except Exception as e:
        print(f"[seed] ✗ Error seeding admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_user()
