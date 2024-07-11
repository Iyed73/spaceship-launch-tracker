from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp, Optional
from sqlalchemy import select
from app import db
from app.models import User, Subscriber


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


class LaunchFilterForm(FlaskForm):
    class Meta:
        csrf = False
    spaceship = SelectField("Spaceship", coerce=int, choices=[])
    launch_site = SelectField("Launch Site", coerce=int, choices=[])
    per_page = SelectField("Launches per Page", coerce=int, choices=[(10, '10'), (20, '20'), (30, '30')], default=10)
    submit = SubmitField("Filter")


class SubscriptionForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Full name", validators=[Length(min=4, max=64), DataRequired(),
                                                Regexp(r'^[a-zA-Z]+$', message="Full name must contain only letters.")])
    submit = SubmitField("Subscribe")

    def validate_email(self, email):
        if self.email.data and self.email.validate(self):
            subscriber = db.session.scalar(select(Subscriber).where(Subscriber.email == email.data))
            if subscriber is not None and subscriber.is_confirmed:
                raise ValidationError("Email is already subscribed.")
