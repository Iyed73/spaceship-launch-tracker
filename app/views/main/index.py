from flask import render_template
from flask.typing import ResponseReturnValue
from flask.views import View


class HomeView(View):
    def dispatch_request(self) -> ResponseReturnValue:
        return render_template("main/home.html")
