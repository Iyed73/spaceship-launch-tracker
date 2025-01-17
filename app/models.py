import enum
from datetime import UTC, datetime, timedelta
from typing import Any, Self
from uuid import UUID, uuid4

from flask import current_app
from flask_login import UserMixin
from itsdangerous import BadData, URLSafeTimedSerializer
from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, UniqueConstraint, not_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship, validates
from sqlalchemy.orm.attributes import get_history
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class TimestampMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime, default=lambda: datetime.now(UTC))

    @declared_attr
    def updated_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime, onupdate=lambda: datetime.now(UTC))


class CreatedByMixin:
    @declared_attr
    def creator_id(cls) -> Mapped[UUID | None]:
        return mapped_column(ForeignKey("users.id"))

    @declared_attr
    def creator(cls) -> Mapped["User | None"]:
        return relationship("User")


class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(128), default="spectator")
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    reminders: Mapped[list["UserReminder"]] = relationship(cascade="all, delete-orphan", back_populates="user")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return self.password_hash is not None and check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(str(self.id), salt=current_app.config["SECURITY_PASSWORD_SALT"])

    def confirm_token(self, token: str, expiration: int = 3600) -> bool:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=expiration)
        except BadData:
            return False
        if data != str(self.id):
            return False
        self.is_confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self) -> str:
        return f'{self.role}({self.id.hex}, "{self.username}", {self.email})'


@login.user_loader
def load_user(id: str) -> User | None:
    return db.session.get(User, UUID(id))


class LaunchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    SCRUBBED = "scrubbed"
    LAUNCHED = "launched"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def transitions(self) -> tuple["LaunchStatus", ...]:
        return LAUNCH_STATUS_TRANSITIONS[self]

    def __str__(self) -> str:
        return self.value


LAUNCH_STATUS_TRANSITIONS: dict[LaunchStatus, tuple[LaunchStatus, ...]] = {
    LaunchStatus.SCHEDULED: (
        LaunchStatus.DELAYED,
        LaunchStatus.SCRUBBED,
        LaunchStatus.LAUNCHED,
        LaunchStatus.CANCELLED,
    ),
    LaunchStatus.DELAYED: (LaunchStatus.SCRUBBED, LaunchStatus.LAUNCHED, LaunchStatus.CANCELLED),
    LaunchStatus.SCRUBBED: (LaunchStatus.SCHEDULED, LaunchStatus.CANCELLED),
    LaunchStatus.LAUNCHED: (LaunchStatus.SUCCEEDED, LaunchStatus.FAILED),
    LaunchStatus.SUCCEEDED: (),
    LaunchStatus.FAILED: (),
    LaunchStatus.CANCELLED: (),
}


class Launch(db.Model, TimestampMixin, CreatedByMixin):
    __tablename__ = "launches"

    TRACKED_FIELDS = ("mission", "description", "launch_timestamp", "spaceship_id", "launch_site_id", "status")

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    mission: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[str | None] = mapped_column(String(1024))
    launch_timestamp: Mapped[datetime]
    status: Mapped[LaunchStatus] = mapped_column(Enum(LaunchStatus), default=LaunchStatus.SCHEDULED)
    version: Mapped[int] = mapped_column(default=1)
    spaceship_id: Mapped[int] = mapped_column(ForeignKey("spaceships.id"), index=True)
    launch_site_id: Mapped[int] = mapped_column(ForeignKey("launch_sites.id"), index=True)

    __mapper_args__ = {"version_id_col": version}

    spaceship: Mapped["Spaceship"] = relationship(lazy="joined", back_populates="launches")

    launch_site: Mapped["LaunchSite"] = relationship(lazy="joined", back_populates="launches")

    launch_reminders: Mapped[list["LaunchReminder"]] = relationship(
        cascade="all, delete-orphan", back_populates="launch"
    )

    user_reminders: Mapped[list["UserReminder"]] = relationship(cascade="all, delete-orphan", back_populates="launch")

    events: Mapped[list["LaunchEvent"]] = relationship(
        cascade="all, delete-orphan", back_populates="launch", order_by="LaunchEvent.id"
    )

    @classmethod
    def get_upcoming_with_no_reminders(cls, now: datetime, time_delta: timedelta) -> list[Self]:
        return (
            db.session.query(cls)
            .filter(
                cls.launch_timestamp.between(now, now + time_delta),
                cls.status.in_([LaunchStatus.SCHEDULED, LaunchStatus.DELAYED]),
                not_(cls.launch_reminders.any()),
            )
            .all()
        )

    @validates("status")
    def validate_status(self, key: str, status: LaunchStatus) -> LaunchStatus:
        if self.status not in (None, status) and status not in self.status.transitions:
            raise ValueError(f"Launch cannot go from {self.status} to {status}")
        return status

    def record_event(self, creator_id: UUID) -> bool:
        changes: dict[str, list[Any]] = {}
        for field in self.TRACKED_FIELDS:
            history = get_history(self, field)
            old = history.deleted[0] if history.deleted else None
            new = history.added[0] if history.added else None
            if old != new:
                changes[field] = [self.serialize(old), self.serialize(new)]
        if changes:
            self.events.append(LaunchEvent(changes=changes, creator_id=creator_id))
        return bool(changes)

    @staticmethod
    def serialize(value: Any) -> Any:
        return value.isoformat() if isinstance(value, datetime) else value

    def __repr__(self) -> str:
        return f"{self.id.hex}: {self.mission}"


class Spaceship(db.Model, TimestampMixin, CreatedByMixin):
    __tablename__ = "spaceships"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    description: Mapped[str | None] = mapped_column(String(1024))
    height: Mapped[float]
    mass: Mapped[float]
    payload_capacity: Mapped[float]
    thrust_at_liftoff: Mapped[float]

    launches: Mapped[list["Launch"]] = relationship(cascade="all, delete-orphan", back_populates="spaceship")

    def __repr__(self) -> str:
        return f"{self.id}: {self.name}"


class LaunchSite(db.Model, TimestampMixin, CreatedByMixin):
    __tablename__ = "launch_sites"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    location: Mapped[str] = mapped_column(String(256))

    launches: Mapped[list["Launch"]] = relationship(cascade="all, delete-orphan", back_populates="launch_site")

    def __repr__(self) -> str:
        return f"{self.id}: {self.name}"


class Subscriber(db.Model, TimestampMixin):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(128))
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    def generate_confirmation_token(self) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.email, salt=current_app.config["SECURITY_PASSWORD_SALT"])


class LaunchReminder(db.Model, TimestampMixin):
    __tablename__ = "launch_reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    launch_id: Mapped[UUID] = mapped_column(ForeignKey("launches.id"), index=True, unique=True)

    launch: Mapped["Launch"] = relationship(lazy="joined", back_populates="launch_reminders")

    @classmethod
    def claim(cls, launch_id: UUID) -> bool:
        statement = (
            insert(cls)
            .values(launch_id=launch_id)
            .on_conflict_do_nothing(index_elements=[cls.launch_id])
            .returning(cls.id)
        )
        return db.session.scalar(statement) is not None


class UserReminder(db.Model, TimestampMixin):
    __tablename__ = "user_reminders"
    __table_args__ = (UniqueConstraint("user_id", "launch_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    launch_id: Mapped[UUID] = mapped_column(ForeignKey("launches.id"), index=True)

    user: Mapped["User"] = relationship(back_populates="reminders")

    launch: Mapped["Launch"] = relationship(back_populates="user_reminders")


class LaunchEvent(db.Model, CreatedByMixin):
    __tablename__ = "launch_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    launch_id: Mapped[UUID] = mapped_column(ForeignKey("launches.id"), index=True)
    changes: Mapped[dict[str, list[Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    launch: Mapped["Launch"] = relationship(back_populates="events")
