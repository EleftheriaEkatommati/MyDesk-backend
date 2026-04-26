# MyDesk Backend API Reference

Base path: `/api/v1`

## Authentication

### POST `/api/v1/auth/register`
- Create a new user account
- Request body:
  - `email`
  - `name`
  - `surname`
  - `password`
- Response: created `User`
- No authentication required

### POST `/api/v1/auth/login`
- Authenticate a user with email and password
- Request body:
  - `email`
  - `password`
- Response:
  - `id`
  - `name`
  - `role`
  - `token`
- No authentication required

### GET `/api/v1/auth/google/login`
- Redirects the browser to Google for OAuth consent
- No authentication required

### GET `/api/v1/auth/google/callback`
- Receives the OAuth `code` from Google
- Exchanges the code for a token and user profile
- Creates a user if needed
- Returns a JWT or redirects to the frontend with `token`

## Admin

These endpoints require admin privileges.

### POST `/api/v1/admin/users`
- Create a new user
- Request body: `UserCreate`
- Response: created `User`

### PUT `/api/v1/admin/users/{user_id}/role`
- Update a user role
- Request body: `RoleUpdate`
- Response: updated `User`

### GET `/api/v1/admin/users`
- List users with pagination
- Query params: `skip`, `limit`
- Response: list of `User`

### DELETE `/api/v1/admin/users/{user_id}`
- Remove a user and their related bookings
- Response: `204 No Content`

### DELETE `/api/v1/admin/bookings/{booking_id}`
- Remove a booking by ID
- Sends notification email if the booking was active
- Response: `204 No Content`

### POST `/api/v1/admin/desks`
- Create a desk
- Request body: `DeskCreate`
- Response: created `Desk`

### PUT `/api/v1/admin/desks/{desk_id}`
- Update desk coordinates or rotation
- Response: updated `Desk`

### DELETE `/api/v1/admin/desks/{desk_id}`
- Delete a desk and cascade-delete related bookings
- Sends email notifications for active bookings
- Response: `204 No Content`

### POST `/api/v1/admin/floors`
- Create a floor
- Request body: `FloorCreate`
- Response: created `Floor`

## Desks & Floors

### GET `/api/v1/desks?date=YYYY-MM-DD`
- Returns all desks with booking status for the requested date
- Response: list of `DeskWithStatusSchema`

### GET `/api/v1/desks/floors`
- Returns all floors
- Response: list of `FloorResponse`

### GET `/api/v1/desks/floors/{floor_id}`
- Returns a single floor
- Response: `FloorResponse`

### POST `/api/v1/desks/{desk_id}/book`
- Book a desk for the current user
- Request body: `BookingCreate`
- Response: created `Booking`

### GET `/api/v1/desks/floors/{floor_id}/desks?booking_date=YYYY-MM-DD`
- Returns desks for a floor with booking status for the requested date
- Response: list of `DeskWithStatusSchema`

## Bookings

### GET `/api/v1/bookings/me`
- List bookings of the current authenticated user
- Optional query param: `date`
- Response: list of `Booking`

### PUT `/api/v1/bookings/{booking_id}/cancel`
- Cancel a booking
- Response: updated `Booking`

### GET `/api/v1/bookings/report/daily?report_date=YYYY-MM-DD`
- Admin-only daily booking report
- Response: booking statistics, checked-in bookings, pending bookings, users without a booking

### POST `/api/v1/bookings/check-in`
- Admin-only endpoint for QR-based check-in
- Request body:
  - `qr_data` formatted as `BOOKING_ID:<id>`
- Response: updated `Booking`

### GET `/api/v1/bookings/attendance?date=YYYY-MM-DD&floor_id=<floor_id>`
- Returns checked-in bookings for a date
- Optional floor filter
- Response: list of `Booking`

## Root

### GET `/`
- Returns a welcome message:

```json
{ "message": "Welcome to the MyDesk API" }
```

## Notes

- Protected endpoints require an `Authorization: Bearer <token>` header.
- Admin-only routes require the authenticated user to have `role == admin`.
