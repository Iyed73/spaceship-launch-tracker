import click
from flask import current_app
from flask.cli import with_appcontext
from rq import Worker


@click.command("worker")
@with_appcontext
def run_worker():
    worker = Worker([current_app.task_queue], connection=current_app.redis)
    worker.work()
