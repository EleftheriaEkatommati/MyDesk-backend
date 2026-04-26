# MyDesk Backend UI Integration

## Frontend connection

- The backend exposes a CORS policy that allows all origins in `main.py`:
  - `allow_origins=["*"]`
  - `allow_methods=["*"]`
  - `allow_headers=["*"]`
- This allows a frontend running on a different domain or port to call the API during development.

## `FRONTEND_URL` usage

- `FRONTEND_URL` is configured in the `.env` file.
- During Google OAuth callback, if `FRONTEND_URL` is set, the backend redirects the browser to:

```text
<FRONTEND_URL>?token=<jwt>
```

- This provides the frontend with the JWT after successful Google login.

## Recommended frontend behavior

- After login, store the JWT in secure browser storage (for example, HTTP-only cookies or local storage based on your security policy).
- Attach the JWT to all protected API requests using the `Authorization: Bearer <token>` header.

## Endpoints useful for UI

- `/api/v1/auth/login` — local email/password login
- `/api/v1/auth/register` — sign-up
- `/api/v1/auth/google/login` — start Google OAuth
- `/api/v1/auth/google/callback` — complete Google OAuth
- `/api/v1/desks?date=YYYY-MM-DD` — show desk availability
- `/api/v1/desks/floors` — load floor list
- `/api/v1/desks/floors/{floor_id}/desks?booking_date=YYYY-MM-DD` — show desks on a floor
- `/api/v1/desks/{desk_id}/book` — book a desk
- `/api/v1/bookings/me` — list user bookings

## Notes on integration

- The backend returns relational objects in responses, such as desk floor metadata and booking desk details.
- The API uses JSON request bodies and responses.
- The root endpoint `/` can be used for a quick health check.
- FastAPI documentation is available at runtime at `/docs` and `/redoc`.
