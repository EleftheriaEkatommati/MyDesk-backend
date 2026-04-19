from database.session import SessionLocal
from models.desk import Desk

def clear_all_desks():
    """
    Deletes all rows from the desks table.
    """
    db = SessionLocal()
    try:
        num_rows_deleted = db.query(Desk).delete()
        db.commit()
        print(f"--- Successfully deleted {num_rows_deleted} desks. ---")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_desks()