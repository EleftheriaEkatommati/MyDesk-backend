from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so that Base has them before create_all() is called
from models.user import User, Role
from models.desk import Desk
