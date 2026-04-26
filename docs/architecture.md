# MyDesk Backend Architecture

## Technology Stack

- **FastAPI** for building the REST API
- **Python 3.10+**
- **PostgreSQL** as the production database
- **SQLAlchemy** for ORM mapping and relationship management
- **Alembic** for schema migrations
- **Poetry** for dependency management
- **JWT** for stateless authentication
- **Google OAuth** for third-party sign-in

## Core Design Decisions

- The backend is organized with separate folders for `api`, `crud`, `models`, `schemas`, `core`, and `database`.
- SQLAlchemy models define the database schema, while Pydantic schemas validate request/response payloads.
- Role-based access control is implemented through `RoleEnum` and a dedicated admin dependency.
- Bookings are designed with explicit `BookingStatus` values: `ACTIVE`, `CANCELLED`, and `CHECKED_IN`.
- Users can only have one role. The system supports two roles:
  - `admin`
  - `user`
- Desks are tied to floors, and bookings are tied to desks and users.
- Admin operations are separated from user operations in the API router structure.

## Data Model and Relationships

### Tables and Entities

- `roles`
  - `id`: primary key
  - `name`: enum value (`admin`, `user`)

- `users`
  - `id`: primary key
  - `email`: unique identifier
  - `name`
  - `surname`
  - `hashed_password`
  - `role_id`: foreign key to `roles.id`

- `floors`
  - `id`: primary key
  - `floor_number`
  - `floor_name`

- `desks`
  - `id`: primary key
  - `x`, `y`, `rotation`
  - `floor_id`: foreign key to `floors.id`

- `bookings`
  - `id`: primary key
  - `user_id`: foreign key to `users.id`
  - `desk_id`: foreign key to `desks.id`
  - `booking_date`
  - `status`: enum value (`ACTIVE`, `CANCELLED`, `CHECKED_IN`)

### Relationships

- `Role` → `User`: one-to-many
- `User` → `Booking`: one-to-many
- `Floor` → `Desk`: one-to-many
- `Desk` → `Booking`: one-to-many
- `Booking` → `User`: many-to-one
- `Booking` → `Desk`: many-to-one

### Cascades and integrity

- Deleting a `Desk` cascades to delete its associated bookings.
- Deleting a `Floor` cascades to delete its desks and their associated bookings.
- `Booking` uses explicit foreign keys to preserve referential integrity.

## Admin Role and Authorization

- Admin authorization is enforced in `core/security.py` using `get_current_active_admin`.
- Any endpoint that requires admin privileges depends on `get_current_active_admin`.
- This dependency checks the authenticated user and verifies `user.role.name == RoleEnum.admin`.
- Admin-only routers include user management, booking deletion, desk management, and floor creation.

## Important Structural Choices

- The backend is built as a pure REST API, leaving UI rendering to the frontend.
- `FastAPI` `APIRouter` is used to keep authentication, admin, desk, and booking routes separate and maintainable.
- The database session is centralized in `database/session.py`, so the same session pattern works across all routers.
- Google OAuth uses direct HTTP requests to Google's token and userinfo endpoints instead of a third-party SDK.
