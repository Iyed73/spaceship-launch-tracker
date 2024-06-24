from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp, Optional
from sqlalchemy import select
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=64),
                                                   Regexp(r'^[\w.@+-_]+$', message="Only alphanumeric characters, "
                                                                                   "dots, '@', '+', '-' and '_' are "
                                                                                   "allowed for username.")])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=64)])
    password_confirmation = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        if self.username.data and self.username.validate(self):
            user = db.session.scalar(select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError("Choose a different username.")

    def validate_email(self, email):
        if self.email.data and self.email.validate(self):
            user = db.session.scalar(select(User).where(User.email == email.data))
            if user is not None:
                raise ValidationError("Email is already used.")


class SpaceshipForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=64)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1024)])
    height = FloatField("Height (m)", validators=[DataRequired()])
    mass = FloatField("Mass (kg)", validators=[DataRequired()])
    payload_capacity = FloatField("Payload Capacity (kg)", validators=[DataRequired()])
    thrust_at_liftoff = FloatField("Thrust at Liftoff (kN)", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LaunchSiteForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=64)])
    location = StringField("Location", validators=[DataRequired(), Length(max=256)])
    submit = SubmitField("Submit")


class LaunchForm(FlaskForm):
    mission = StringField("Mission", validators=[DataRequired(), Length(max=128)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1024)])
    launch_timestamp = DateTimeField(
        "Launch Timestamp",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
        render_kw={"type": "datetime-local"}
    )
    spaceship_id = SelectField("Spaceship", coerce=int, choices=[])
    launch_site_id = SelectField("Launch Site", coerce=int, choices=[])
    submit = SubmitField("Submit")

