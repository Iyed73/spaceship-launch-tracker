from flask import render_template, request
from flask.views import MethodView
from datetime import datetime
from app.models import Launch, Spaceship, LaunchSite
from app.forms import LaunchFilterForm


class PastLaunchesView(MethodView):
    def get(self):
        now = datetime.now()
        page = request.args.get("page", 1, type=int)

        form = LaunchFilterForm(request.args)

        per_page = form.per_page.data or 10

        form.spaceship.choices = ([(0, "All Spaceships")] +
                                  [(spaceship.id, spaceship.name) for spaceship in Spaceship.query.all()])
        form.launch_site.choices = ([(0, "All Launch Sites")] +
                                    [(site.id, site.name) for site in LaunchSite.query.all()])

        query = Launch.query.filter(Launch.launch_timestamp <= now)

        if form.spaceship.data and form.spaceship.data is not 0:
            query = query.filter(Launch.spaceship_id == form.spaceship.data)

        if form.launch_site.data and form.launch_site.data is not None:
            query = query.filter(Launch.launch_site_id == form.launch_site.data)

        pagination = query.order_by(Launch.launch_timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
        launches = pagination.items

        spaceships = Spaceship.query.all()
        launch_sites = LaunchSite.query.all()

        return render_template(
            "launches/launches_list.html",
            launches=launches,
            pagination=pagination,
            spaceships=spaceships,
            launch_sites=launch_sites,
            form=form,
            status="Past"
        )
