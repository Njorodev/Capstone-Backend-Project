from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models.models as models

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Check if we already have courses
    if db.query(models.Course).count() > 0:
        print("Database already has data. Skipping seed.")
        return

    print("Seeding 20 demo courses...")
    for i in range(1, 21):
        course = models.Course(
            title=f"Advanced Python {i}01",
            code=f"PY{100 + i}",
            capacity=10 + i,
            is_active=True,
            deleted_at=None  # Matches your model's column name
        )
        db.add(course)
    
    db.commit()
    print("Seeding complete! Run your server and check /courses?limit=5")
    db.close()

if __name__ == "__main__":
    seed_data()