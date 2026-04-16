import argparse

from database.session import SessionLocal
from models.user import User


def delete_user_by_email(email: str) -> int:
    db = SessionLocal()
    try:
        deleted_count = db.query(User).filter(User.email == email).delete(synchronize_session=False)
        db.commit()
        return deleted_count
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a seeded user by email.")
    parser.add_argument(
        "--email",
        default="riaekato@gmail.com",
        help="Email address of the user to delete.",
    )
    args = parser.parse_args()

    deleted = delete_user_by_email(args.email)
    if deleted:
        print(f"Deleted {deleted} user(s) with email {args.email}.")
    else:
        print(f"No user found with email {args.email}.")
