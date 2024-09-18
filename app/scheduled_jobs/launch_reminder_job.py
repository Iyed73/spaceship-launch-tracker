from app.tasks.event_categories import EventCategory
from sqlalchemy import not_
from datetime import datetime, timedelta


def remind_subscribers():
    from app.tasks.process_event import process_subscribers_event
    from app.models import Launch, LaunchEvent
    from app import app, db
    with app.app_context():
        now = datetime.utcnow()
        launches = (db.session.query(Launch)
                    .filter(Launch.launch_timestamp.between(now, now + timedelta(hours=2)),
                            not_(Launch.launch_events.any(LaunchEvent.category == EventCategory.REMINDER)
                                 )).all())
        for launch in launches:
            job = app.task_queue.enqueue(process_subscribers_event, EventCategory.REMINDER, launch=launch)
            event = LaunchEvent(id=job.get_id(), name=f"launch reminder: {launch.mission}", launch=launch, category=EventCategory.REMINDER)
            db.session.add(event)
            db.session.commit()
