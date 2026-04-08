from database.session import SessionLocal
from database.session import engine
from database.base import Base
from models.desk import Desk

def seed_desks():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        desks_data = [
            # Cluster 1
            {"id": "101", "x": 60, "y": 80, "rotation": 180},
            {"id": "102", "x": 150, "y": 80, "rotation": 180},
            {"id": "103", "x": 60, "y": 160, "rotation": 0},
            {"id": "104", "x": 150, "y": 160, "rotation": 0},
            
            # Cluster 2
            {"id": "201", "x": 360, "y": 250, "rotation": 180},
            {"id": "202", "x": 450, "y": 250, "rotation": 180},
            {"id": "203", "x": 360, "y": 330, "rotation": 0},
            {"id": "204", "x": 450, "y": 330, "rotation": 0},
            
            # Private Office
            {"id": "301", "x": 80, "y": 460, "rotation": 90},
        ]

        for desk_dict in desks_data:
            existing = db.query(Desk).filter(Desk.id == desk_dict["id"]).first()
            if not existing:
                new_desk = Desk(**desk_dict)
                db.add(new_desk)
                
        db.commit()
        print("Desks seeded successfully!")
    except Exception as e:
        print(f"Error seeding desks: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_desks()