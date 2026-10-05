# WORD//TRACE — Django Conversion

This is a Django conversion of the supplied **Guess the Word / WORD//TRACE** project.

The original implementation used Spring Boot + JPA + H2 for the backend and React + Vite for the frontend. This version keeps the same game rules, API shape, page styling, authentication flow, player/admin behavior, and word evaluation logic, while replacing the application layer with Django.

## Stack

- **Backend:** Django + Django ORM
- **Authentication:** JWT using PyJWT
- **Frontend:** Django templates + vanilla JavaScript
- **Database:** SQLite (`data/guessword.sqlite3`)
- **Timezone:** Asia/Kolkata

## Preserved behavior

### Player

- Register with username validation: 5–40 letters only.
- Password validation: minimum 5 characters, at least one letter, one number, and `$`, `%`, or `*`.
- JWT login and role-based authorization.
- Start/resume a round.
- Maximum 3 started rounds per day.
- Random five-letter target from the database.
- Maximum 5 guesses per round.
- Exact match = green.
- Correct letter in another position = orange.
- Letter absent = grey.
- Duplicate-letter handling matches the original two-pass evaluation algorithm.
- Correct guess ends the round with `CONGRATULATIONS! You found the word.`
- Fifth failed guess ends the round with `BETTER LUCK NEXT TIME!`.
- Previous guesses and tile results persist in the database.

### Admin

- Seeded admin login: `admin` / `Admin1*`.
- Daily report: distinct users + number of games won.
- User report: date + words tried + correct guesses.
- Word bank management: add/delete five-letter words.
- Words already attached to games cannot be deleted.
- At least one word must remain configured.

## Run locally

From this directory:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the database:

```bash
python manage.py migrate
```

The seed-data migration creates the original 20-word bank and the `admin` / `Admin1*` demo account. If you previously ran the broken package and `gameapp.0002_seed_data` failed, simply fix the migration as in this package and run `python manage.py migrate` again; Django will retry the still-unapplied migration. The idempotent seed command is also available:

```bash
python manage.py seed_data
```

Start the app:

```bash
python manage.py runserver 8000
```

Open `http://127.0.0.1:8000/`.

## Environment

Copy `.env.example` to `.env` and export those values using your preferred environment-variable mechanism. At minimum, replace the development JWT secret before deployment.

## API compatibility

The original REST paths are intentionally preserved:

```text
POST   /api/auth/register
POST   /api/auth/login
GET    /api/game/status
POST   /api/game/start
GET    /api/game/{gameId}
POST   /api/game/{gameId}/guess
GET    /api/admin/reports/day?date=YYYY-MM-DD
GET    /api/admin/reports/user/{username}
GET    /api/admin/words
POST   /api/admin/words
DELETE /api/admin/words/{id}
```

Authenticated requests continue to use:

```text
Authorization: Bearer <JWT>
```

## Project structure

```text
guess-word-game-django/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── gameapp/
│   ├── migrations/
│   ├── management/commands/seed_data.py
│   ├── authentication.py
│   ├── models.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/styles.css
│   └── js/
├── templates/
├── data/
├── manage.py
├── requirements.txt
└── README.md
```

## Important conversion note

The UI is no longer a separate React/Vite application. Django serves the same visual interface and the browser-side interaction is handled by small vanilla-JS files. This removes the Node/React build step while retaining the original REST API contract and behavior.

The supplied H2 database is not copied directly into SQLite because H2 and SQLite have different database formats. The original demo word bank and admin account are recreated by `seed_data`; existing player/game history would need a one-time data migration if you need it preserved exactly.

### Updating from an earlier broken build
If you already have a database created by an earlier Django build, run:

```bash
python manage.py migrate
```

The `0003_add_guess_date_joined` migration adds the missing `Guess.date_joined` column that older builds accidentally omitted from `0001_initial`.
