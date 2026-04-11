from database.session import SessionLocal
from models.booking import Booking

def clear_all_bookings():
    """
    Deletes all rows from the bookings table.
    """
    db = SessionLocal()
    try:
        num_rows_deleted = db.query(Booking).delete()
        db.commit()
        print(f"--- Successfully deleted {num_rows_deleted} rows from the bookings table. ---")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_bookings()