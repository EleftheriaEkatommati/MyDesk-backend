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

The project includes several scripts to initialize and manage the database state for development and testing purposes.

#### Initial Data Seeding

The primary script for populating the database with initial data is `seed_db.py`. It should be run after applying database migrations.

```bash
poetry run python seed_db.py
```

This script performs the following actions:
- **Depends on `dummy_data.json`**: It reads this file from the project root for initial data.
- **Seeds Core Data**: It populates the `roles`, `users`, and `floors` tables. It checks for existing records by ID to avoid creating duplicates on subsequent runs.
- **Seeds Desks**: It populates the `desks` table *only if it is empty*. This prevents adding more desks if the script is run again.
- **Assigns Roles**: It links users to their roles.
- **Resets Sequences**: It resets the auto-incrementing ID counters for tables where data was inserted with specific IDs (`users`, `roles`, `floors`). This is crucial to prevent primary key conflicts when the application's API starts creating new records.

#### Other Data Management Scripts

Several other scripts are available for more granular control over the database state:
- **`drop_db.py`**: Drops all tables from the database. This is a destructive action and should be used with care, typically before re-running all migrations and seeding from scratch.
- **`seed_desks.py`**: An alternative script to populate `floors` and `desks` tables with a hardcoded set of data. It also creates initial `bookings` for today's date. This can be useful for specific testing scenarios.
- **`clear_desks.py`**: Deletes all records from the `desks` table.
- **`clear_bookings.py`**: Deletes all records from the `bookings` table.
- **`delete_user_seed.py`**: A command-line script to delete a user by email address.

## Notes

- The current Docker Compose file does not automatically start the backend service.
- In production, CORS should be restricted to known frontend origins, not `*`.
- The `DATABASE_URL` in `.env` should use the proper host and port from your deployment environment.

## Database Backup and Restore

You can create a backup of your database from the running Docker container and another user can use this backup to initialize their environment.

### Exporting the Database

To export the data from the `db` service into a SQL file, you first need to ensure your Docker Compose stack is running (`docker compose up`).

Then, run the following command from your project's root directory. This command executes `pg_dump` inside the `db` container and saves the output to a `mydesk_backup.sql` file on your local machine.

You will need to replace `<YOUR_DB_USER>` and `<YOUR_DB_NAME>` with the values from your `.env` file (e.g., `POSTGRES_USER` and `POSTGRES_DB`).

```bash
docker compose exec -T db pg_dump -U <YOUR_DB_USER> -d <YOUR_DB_NAME> > mydesk_backup.sql
```

You can now share the `mydesk_backup.sql` file.

### Importing the Database

Another user can use the `mydesk_backup.sql` file to initialize their database when they start their Docker Compose stack for the first time. This is done by using the PostgreSQL image's entrypoint initialization feature.

1.  **Create an `init-db` directory** in the project root and place the `mydesk_backup.sql` file inside it.

2.  **Modify `docker-compose.yml`**: Add a volume mount to the `db` service that maps the `init-db` directory on your host to the `/docker-entrypoint-initdb.d` directory inside the container.

    ```yaml
    services:
      db:
        # ... other db service configuration ...
        volumes:
          - ./postgres_data:/var/lib/postgresql/data
          - ./init-db:/docker-entrypoint-initdb.d
    ```

3.  **Start with a clean volume**: The initialization script only runs when the database volume is empty. If you have run `docker compose up` before, you must first remove the old database volume with `docker compose down -v`.

4.  **Start the stack**: Now, bring the stack up with `docker compose up --build`. The PostgreSQL container will start, find the `.sql` file, and execute it to populate the database.
