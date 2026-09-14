# Ticket System API (FastAPI + MySQL)

## Setup

1. Create the MySQL database (do this once, before running the app):
   ```sql
   CREATE DATABASE ticket_system CHARACTER SET utf8mb4;
   ```

2. Copy `.env.example` to `.env` and fill in your MySQL credentials:
   ```
   cp .env.example .env
   ```

3. Create and activate a virtual environment, then install dependencies:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   If you already have the project venv, activate it again after every terminal restart:
   ```
   source .venv/bin/activate
   ```

4. Run the server:
   ```
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The app will create the MySQL database and tables automatically on first run.

5. Open http://localhost:8000/docs for interactive Swagger docs to test every endpoint.

## Endpoints

| Method | Path                          | Purpose                                              |
|--------|-------------------------------|-------------------------------------------------------|
| POST   | /auth/register                | Sign up a new BA                                       |
| POST   | /auth/login                   | Login (no token — returns user object to store locally)|
| GET    | /users/{id}                   | View profile                                           |
| PUT    | /users/{id}                   | Update profile                                         |
| POST   | /tickets                      | Create ticket(s). app_type="both" creates 2 tickets    |
| GET    | /tickets                      | List all tickets, or ?user_id= for one BA's tickets    |
| GET    | /tickets/{ticket_number}      | Get one ticket (Flask detail page uses this)           |
| PUT    | /tickets/{ticket_number}      | Full edit (Flask dev UI / Flutter update page)         |
| PATCH  | /tickets/{ticket_number}/status | Quick status-only update                             |

## Notes / decisions made per your requirements

- No JWT/auth tokens. Login just validates credentials and returns the user
  row; Flutter is expected to keep that in local storage until logout.
- `app_type` is `android` / `ios` (not a 1/0 bit) since "both" splits into two
  real rows anyway — an enum is clearer to work with than a flag once you're
  already creating separate tickets.
- `(sub_domain, app_type)` is the unique constraint, not `sub_domain` alone —
  otherwise creating both an Android and iOS ticket for the same operator
  would fail on the second insert.
- `ticket_number` (e.g. `TCK-000001`) is what the Flask app will use in its
  URL (`/ticket/TCK-000001`), not the raw numeric `id`.
- Flask has no login per your instruction — anyone with the ticket URL can
  view/update it. You can add auth to Flask later without touching this API.
- Images are 6 plain URL columns (no file upload) as agreed — easy to migrate
  to a child table later if you need more than 6 or want file uploads.
