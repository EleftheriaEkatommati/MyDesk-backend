from database.base import Base
from database.session import engine

Base.metadata.drop_all(bind=engine)