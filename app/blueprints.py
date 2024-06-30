from flask import Blueprint


authentication_bp = Blueprint("authentication", __name__)
main_bp = Blueprint("main", __name__)
mission_control_bp = Blueprint("mission_control", __name__)
launches_bp = Blueprint("launches", __name__)
