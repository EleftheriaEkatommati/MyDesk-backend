from database.session import SessionLocal
from database.session import engine
from database.base import Base
from models.desk import Desk
from models.booking import Booking
from models.floor import Floor
from datetime import date

FLOORS = [
    {"floor_number": 1, "floor_name": "1st Floor"},
    {"floor_number": 2, "floor_name": "2nd Floor"},
    {"floor_number": 3, "floor_name": "3rd Floor"},
]

DESKS_DATA = [
    # Cluster 1
    {"id": "101", "x": 60, "y": 80, "rotation": 180, "floor": "1st Floor"},
    {"id": "102", "x": 150, "y": 80, "rotation": 180, "floor": "1st Floor"},
    {"id": "103", "x": 60, "y": 160, "rotation": 0, "floor": "1st Floor"},
    {"id": "104", "x": 150, "y": 160, "rotation": 0, "floor": "1st Floor"},

    # Cluster 2
    {"id": "201", "x": 360, "y": 250, "rotation": 180, "floor": "2nd Floor"},
    {"id": "202", "x": 450, "y": 250, "rotation": 180, "floor": "2nd Floor"},
    {"id": "203", "x": 360, "y": 330, "rotation": 0, "floor": "2nd Floor"},
    {"id": "204", "x": 450, "y": 330, "rotation": 0, "floor": "2nd Floor"},

    # Private Office
    {"id": "301", "x": 80, "y": 460, "rotation": 90, "floor": "3rd Floor"},
]

# Desks to book initially
BOOKED_DESKS = [
    {"id": "101", "booked_by": 1},
    {"id": "102", "booked_by": 1},
    {"id": "201", "booked_by": 2},
    {"id": "104", "booked_by": 2},
]


def seed_desks():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        floor_map = {}
        for floor_data in FLOORS:
            floor = db.query(Floor).filter(Floor.floor_name == floor_data["floor_name"]).first()
            if not floor:
                floor = Floor(**floor_data)
                db.add(floor)
                db.flush()
            floor_map[floor.floor_name] = floor.id

        for desk_dict in DESKS_DATA:
            existing = db.query(Desk).filter(Desk.id == desk_dict["id"]).first()
            if not existing:
                floor_name = desk_dict.pop("floor")
                floor_id = floor_map.get(floor_name)
                if floor_id is None:
                    raise ValueError(f"No floor found for {floor_name}")
                new_desk = Desk(**desk_dict, floor_id=floor_id)
                db.add(new_desk)

        # Book some desks by creating Booking records for today
        today = date.today()
        for booked in BOOKED_DESKS:
            # Check if a booking already exists for this desk on this day to avoid duplicates
            existing_booking = db.query(Booking).filter_by(desk_id=booked["id"], booking_date=today).first()
            if not existing_booking:
                new_booking = Booking(
                    desk_id=booked["id"],
                    user_id=booked["booked_by"],
                    booking_date=today
                )
                db.add(new_booking)

        db.commit()
        print("Desks and floors seeded successfully!")
    except Exception as e:
        print(f"Error seeding desks: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_desks()