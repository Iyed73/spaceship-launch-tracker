import click
from flask.cli import with_appcontext

from app import scheduler


@click.command("scheduler")
@with_appcontext
def run_scheduler() -> None:
    # Importing the module registers the job with the scheduler
    from app.scheduled_jobs.launch_reminder_job import remind_subscribers  # noqa: F401

    # scheduler.start() does nothing in debug mode outside the reloader
    scheduler.scheduler.start()
