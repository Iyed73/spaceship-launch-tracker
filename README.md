A Flask web app for tracking spaceship launches. Admins manage spaceships, launch sites and launches from a mission control panel. Visitors browse upcoming and past launches, subscribe to email updates and set reminders for the launches they care about.

Stack: Flask, SQLAlchemy, PostgreSQL, Redis, RQ, APScheduler, pytest.

## Features

- **Accounts**: registration, login and email confirmation, with `admin` and `spectator` roles.
- **Mission control**: CRUD for spaceships, launch sites and launches (admin only).
- **Launch lists**: upcoming and past launches with filters and pagination.
- **Launch lifecycle**: a launch moves through statuses (scheduled, delayed, scrubbed, launched, succeeded, failed, cancelled) and only valid transitions are accepted.
- **Change history**: every create, update and cancel is stored as an event with the old and new values.
- **Email subscriptions**: double opt-in, then notifications when a launch is created, updated or cancelled.
- **Reminders**: signed-in users set reminders on individual launches, see them on a "My Launches" page and get an email about 2 hours before liftoff.
- **Rate limiting**: a Redis rate limiter with fixed window, sliding window and token bucket strategies.

## Design decisions

**Emails go through a background queue.** Requests only enqueue a job in RQ. A worker then fans out one job per recipient, each with its own retries. The admin's request stays fast and one bad address does not block the others.

**The reminder job runs exactly once per launch.** The scheduler is a separate process (`flask scheduler`), so running several web workers does not multiply the job. A Redis lock skips overlapping runs, and each launch is claimed with `INSERT ... ON CONFLICT DO NOTHING` on a unique `launch_id`. The database claim is what guarantees correctness, so a reminder is never sent twice even if the lock expires.

**Launch edits use optimistic locking.** Each launch has a `version` column that is checked on update. Conflicting edits are rare, so this avoids holding a row lock while an admin fills in a form, and a stale save is rejected instead of silently overwriting someone else's change.

**Status rules live in the model.** Transitions are validated in a SQLAlchemy validator, so an invalid change is rejected no matter which view makes it. Launches are cancelled instead of deleted, which keeps their history.

**The rate limiter is built on a strategy interface.** The algorithm is selected with `RATE_LIMIT_STRATEGY`, without touching the views. Sliding window and token bucket run as Lua scripts so the read and update are atomic in Redis.

**SMTP and Redis failures are handled, not raised.** A registration is rolled back if the confirmation email cannot be sent. A launch change is still saved if the queue is unavailable, and the admin gets a warning that subscribers were not notified.

## Running locally

```bash
docker compose up -d                 # PostgreSQL and Redis
cp .env.example .env                 # then fill in the mail settings
pip install -r requirements.txt
flask db upgrade
flask seed                           # admin user and sample data

flask run                            # web app
flask worker                         # email worker
flask scheduler                      # reminder job
```
