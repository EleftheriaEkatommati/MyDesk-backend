# MyDesk Backend Authentication

## Local Authentication

The backend supports classic email/password signup and login.

### Register

- Endpoint: `POST /api/v1/auth/register`
- Creates a new user with the `user` role
- Passwords are hashed using `bcrypt` via `passlib`
- A default role is assigned from the `roles` table

### Login

- Endpoint: `POST /api/v1/auth/login`
- Accepts:
  - `email`
  - `password`
- Verifies the password with `verify_password`
- Issues a JWT using `create_access_token`

### JWT structure

- The JWT payload includes:
  - `sub`: user email
  - `exp`: expiration timestamp
- Tokens are signed with `SECRET_KEY` and `ALGORITHM`
- The token validity is configured by `ACCESS_TOKEN_EXPIRE_MINUTES`

### Protected endpoints

- The `OAuth2PasswordBearer` token scheme is configured with `tokenUrl="/api/v1/auth/login"`
- `get_current_user` decodes the JWT and loads the user from the database
- `get_current_active_admin` checks that the authenticated user has `RoleEnum.admin`

## Admin Authorization

- Admin-only endpoints depend on `get_current_active_admin`
- This helper throws a `403 Forbidden` if the authenticated user is not an admin
- Admin authorization is enforced for user management, desk and floor management, booking deletion, check-in, and reports

## Google OAuth Integration

### Flow

1. The user visits `GET /api/v1/auth/google/login`
2. The backend redirects to Google's OAuth consent endpoint
3. Google returns an authorization `code` to the callback endpoint
4. The backend exchanges the code for an access token at `https://oauth2.googleapis.com/token`
5. The backend fetches user profile data from `https://openidconnect.googleapis.com/v1/userinfo`
6. If the user email does not exist, the backend creates a new user account with a random password
7. The backend issues a JWT and returns it or redirects to the frontend

### Callback behavior

- Endpoint: `GET /api/v1/auth/google/callback`
- Required query param: `code`
- Optional query param: `error`
- If `FRONTEND_URL` is set, the backend redirects the user to:
  - `FRONTEND_URL?token=<jwt>`
- If `FRONTEND_URL` is not set, the backend returns a JSON response with the JWT

### Required Google settings

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`

> Note: The redirect URI configured in the Google Cloud Console must match `GOOGLE_OAUTH_REDIRECT_URI`.

## Important details

- Google accounts are mapped to the `users` table by email.
- Google-authenticated users still receive a local JWT for all subsequent API requests.
- Because the system stores `hashed_password` for every user, Google-only users are created with a random hashed password.
- The app treats Google users as normal users unless their role is explicitly updated to `admin`.
