# MyDesk Backend Deployment

## Runtime Environment

- Python 3.10+
- PostgreSQL 13 (configured via Docker Compose by default)
- Poetry for dependency management

## Environment Variables

The application loads configuration from the `.env` file via `pydantic-settings` in `core/config.py`.

Required variables:

- `DATABASE_URL` — PostgreSQL database URL
- `SECRET_KEY` — JWT signing secret
- `ALGORITHM` — JWT algorithm (for example `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` — JWT expiration window
- `MAIL_USERNAME` — email account username for notifications
- `MAIL_PASSWORD` — email account password for notifications
- `MAIL_FROM` — sender email address
- `MAIL_SERVER` — SMTP server host
- `MAIL_PORT` — SMTP port
- `MAIL_STARTTLS` — whether to use STARTTLS
- `MAIL_SSL_TLS` — whether to use SSL/TLS
- `USE_CREDENTIALS` — whether to use SMTP authentication
- `GOOGLE_CLIENT_ID` — Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` — Google OAuth client secret
- `GOOGLE_OAUTH_REDIRECT_URI` — callback URI for Google OAuth
- `FRONTEND_URL` — frontend callback URL used after Google login

Example `.env` values are available in `.env.example`.

## Running Locally

1. Install dependencies:

```bash
poetry install
```

2. Create `.env` from `.env.example` and update values:

```bash
cp .env.example .env
```

3. Run migrations:

```bash
poetry run alembic upgrade head
```

4. Seed initial data:

```bash
poetry run python seed_db.py
```

5. Start the API server:

```bash
poetry run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Docker Compose Setup

The repository includes `docker-compose.yml` with services for PostgreSQL and pgAdmin.

### Default services

- `db`: PostgreSQL 13
  - exposed on host port `5433`
- `pgadmin`: pgAdmin 4
  - exposed on host port `5050`

### Enable backend container

The backend service is commented out in `docker-compose.yml`. To run the backend via Docker Compose:

1. Uncomment the `backend` service block.
2. Ensure the `.env` file provides the correct database credentials.
3. Start the stack:

```bash
docker compose up --build
```

### Environment mapping

The backend service should use the same `.env` file and connect to `db` on the Compose network.

## Database and Migrations

### Database technology

- PostgreSQL stores users, roles, floors, desks, and bookings.
- The app connects using SQLAlchemy `create_engine(settings.DATABASE_URL)`.
- Sessions are created with `sessionmaker(autocommit=False, autoflush=False)`.

### Alembic migrations

- Migration scripts are stored under `alembic/versions/`.
- To create a new migration after schema changes:

```bash
poetry run alembic revision --autogenerate -m "Describe change"
```

- To apply migrations:

```bash
poetry run alembic upgrade head
```

### Handling schema changes

1. Update the SQLAlchemy model in `models/`.
2. Generate an Alembic revision.
3. Review and commit the migration script.
4. Apply migrations to the target database.

### Seed data workflow

- `seed_db.py` loads `dummy_data.json` and seeds roles, users, floors, desks, and user-role assignments.
- It also resets PostgreSQL sequences to prevent ID conflicts after manual inserts.

## Notes

- The current Docker Compose file does not automatically start the backend service.
- In production, CORS should be restricted to known frontend origins, not `*`.
- The `DATABASE_URL` in `.env` should use the proper host and port from your deployment environment.
