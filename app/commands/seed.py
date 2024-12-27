import click
from datetime import datetime, timedelta
from flask.cli import with_appcontext
from sqlalchemy import select
from app import db
from app.models import User, Spaceship, LaunchSite, Launch


SPACESHIPS = [
    {"name": "Falcon 9", "description": "Partially reusable two-stage medium-lift launch vehicle.",
     "height": 70, "mass": 549054, "payload_capacity": 22800, "thrust_at_liftoff": 7607},
    {"name": "Falcon Heavy", "description": "Partially reusable heavy-lift launch vehicle.",
     "height": 70, "mass": 1420788, "payload_capacity": 63800, "thrust_at_liftoff": 22819},
    {"name": "Starship", "description": "Fully reusable super heavy-lift launch vehicle.",
     "height": 121, "mass": 5000000, "payload_capacity": 150000, "thrust_at_liftoff": 74400},
    {"name": "Electron", "description": "Two-stage small-lift launch vehicle.",
     "height": 18, "mass": 13000, "payload_capacity": 300, "thrust_at_liftoff": 224},
]

LAUNCH_SITES = [
    {"name": "Kennedy Space Center LC-39A", "location": "Florida, USA"},
    {"name": "Vandenberg SLC-4E", "location": "California, USA"},
    {"name": "Starbase", "location": "Texas, USA"},
    {"name": "Rocket Lab LC-1", "location": "Mahia Peninsula, New Zealand"},
]

LAUNCHES = [
    {"mission": "Aurora-1", "description": "Earth observation satellite deployment.",
     "spaceship": "Falcon 9", "launch_site": "Vandenberg SLC-4E", "days_from_now": -45},
    {"mission": "Deep Relay", "description": "Geostationary communications satellite.",
     "spaceship": "Falcon Heavy", "launch_site": "Kennedy Space Center LC-39A", "days_from_now": -12},
    {"mission": "Kiwi Cubes", "description": "Rideshare of six research cubesats.",
     "spaceship": "Electron", "launch_site": "Rocket Lab LC-1", "days_from_now": -3},
    {"mission": "Orbital Depot Demo", "description": "In-orbit propellant transfer demonstration.",
     "spaceship": "Starship", "launch_site": "Starbase", "days_from_now": 2},
    {"mission": "Aurora-2", "description": "Second Earth observation satellite of the Aurora constellation.",
     "spaceship": "Falcon 9", "launch_site": "Vandenberg SLC-4E", "days_from_now": 9},
    {"mission": "Lunar Pathfinder", "description": "Robotic lander bound for the lunar south pole.",
     "spaceship": "Falcon Heavy", "launch_site": "Kennedy Space Center LC-39A", "days_from_now": 30},
]


def get_or_create(model, defaults=None, **filters):
    instance = db.session.scalar(select(model).filter_by(**filters))
    if instance is None:
        instance = model(**{**(defaults or {}), **filters})
        db.session.add(instance)
    return instance


@click.command("seed")
@click.option("--admin-password", envvar="ADMIN_PASSWORD", prompt=True, hide_input=True)
@with_appcontext
def seed(admin_password):
    admin = get_or_create(User, username="admin",
                          defaults={"email": "admin@launchvault.com", "role": "admin", "is_confirmed": True})
    if admin.password_hash is None:
        admin.set_password(admin_password)

    spaceships = {data["name"]: get_or_create(Spaceship, name=data["name"], defaults={**data, "creator": admin})
                  for data in SPACESHIPS}
    launch_sites = {data["name"]: get_or_create(LaunchSite, name=data["name"], defaults={**data, "creator": admin})
                    for data in LAUNCH_SITES}

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    for data in LAUNCHES:
        get_or_create(Launch, mission=data["mission"],
                      defaults={"description": data["description"],
                                "launch_timestamp": now + timedelta(days=data["days_from_now"]),
                                "spaceship": spaceships[data["spaceship"]],
                                "launch_site": launch_sites[data["launch_site"]],
                                "creator": admin})

    db.session.commit()
    click.echo(f"Seeded {len(spaceships)} spaceships, {len(launch_sites)} launch sites and {len(LAUNCHES)} launches.")
