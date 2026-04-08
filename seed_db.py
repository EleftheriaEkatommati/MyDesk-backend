import json
from database.session import SessionLocal
from database.session import engine
from database.base import Base
from models.user import User, Role, RoleEnum

def seed():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
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
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            if not existing_user:
                user = User(
                    id=user_data['id'],
                    email=user_data['email'],
                    name=user_data['name'],
                    hashed_password=user_data['hashed_password']
                )
                db.add(user)
        db.commit()

        # Seed User Roles (Many-to-Many Relationship)
        for ur_data in data['user_roles']:
            user = db.query(User).filter(User.id == ur_data['user_id']).first()
            role = db.query(Role).filter(Role.id == ur_data['role_id']).first()
            
            if user and role:
                if role not in user.roles:
                    user.roles.append(role)
        db.commit()
        
        print("Database seeded successfully with dummy_data.json!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
