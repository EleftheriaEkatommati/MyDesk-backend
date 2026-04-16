import json
from sqlalchemy import text
from database.session import SessionLocal
from database.session import engine
from database.base import Base
from models.user import User, Role, RoleEnum
from models.floor import Floor
from models.desk import Desk
from core.security import get_password_hash

FLOORS = [
    {"id": 1, "floor_number": 1, "floor_name": "1st Floor"},
    {"id": 2, "floor_number": 2, "floor_name": "2nd Floor"},
    {"id": 3, "floor_number": 3, "floor_name": "3rd Floor"},
]

def seed():
    db = SessionLocal()
    try:
        with open('dummy_data.json', 'r') as f:
            data = json.load(f)
            
        # Seed Roles
        for role_data in data['roles']:
            existing_role = db.query(Role).filter(Role.id == role_data['id']).first()
            if not existing_role:
                # Convert the string name to the RoleEnum
                role_enum_val = RoleEnum.admin if role_data['name'] == 'admin' else RoleEnum.user
                role = Role(id=role_data['id'], name=role_enum_val)
                db.add(role)
        db.commit()

        # Seed Users
        for user_data in data['users']:
            existing_user = db.query(User).filter(User.id == user_data['id']).first()
            if not existing_user:
                user = User(
                    id=user_data['id'],
                    email=user_data['email'],
                    name=user_data['name'],
                    surname=user_data.get('surname'),
                    hashed_password=get_password_hash(user_data['password'])
                )
                db.add(user)
        db.commit()

        # Seed Floors
        for floor_data in FLOORS:
            existing_floor = db.query(Floor).filter(Floor.id == floor_data['id']).first()
            if not existing_floor:
                floor = Floor(**floor_data)
                db.add(floor)
        db.commit()

        # Seed Desks
        for desk_data in data['desks']:
            existing_desk = db.query(Desk).filter(Desk.id == desk_data['id']).first()
            if not existing_desk:
                desk = Desk(**desk_data)
                db.add(desk)
        db.commit()


        # Assign User Roles (One-to-Many Relationship)
        for ur_data in data['user_roles']:
            user = db.query(User).filter(User.id == ur_data['user_id']).first()
            # Since a user can now only have one role, we just assign it.
            # If a user has multiple roles in dummy_data, the last one will be set.
            if user:
                user.role_id = ur_data['role_id']
        db.commit()

        # Reset sequences so auto-generated IDs do not collide with explicit seed IDs
        db.execute(text("SELECT setval(pg_get_serial_sequence('users','id'), (SELECT MAX(id) FROM users))"))
        db.execute(text("SELECT setval(pg_get_serial_sequence('roles','id'), (SELECT MAX(id) FROM roles))"))
        db.execute(text("SELECT setval(pg_get_serial_sequence('floors','id'), (SELECT MAX(id) FROM floors))"))
        db.commit()
        
        print("Database seeded successfully with dummy_data.json!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
