from typing import Optional
from sqlalchemy import func,  String, Integer, ForeignKey, Table, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship, WriteOnlyMapped
from app import db
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))


class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    password_hash = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(String(128), unique=True, default='user')

    def __repr__(self):
        return f'{self.role}({self.id.hex}, "{self.username}", {self.email})'


class RocketLaunch(db.Model, TimestampMixin):
    __tablename__ = 'rocket_launches'

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    mission: Mapped[String] = mapped_column(String(128), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    launch_timestamp: Mapped[datetime]
    rocket_id: Mapped[int] = mapped_column(ForeignKey('rockets.id'), index=True)
    launch_site_id: Mapped[int] = mapped_column(ForeignKey('launch_sites.id'), index=True)

    rocket: Mapped['Rocket'] = relationship(
        lazy='joined', back_populates='rocket_launches'
    )

    launch_site: Mapped['LaunchSite'] = relationship(
        lazy='joined', back_populates='rocket_launches'
    )

    def __repr__(self):
        return f"Rocket({self.id.hex},{self.mission})"


class Rocket(db.Model, TimestampMixin):
    __tablename__ = 'rockets'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    height: Mapped[float]
    mass: Mapped[float]
    payload_capacity: Mapped[float]
    thrust_at_liftoff: Mapped[float]

    rocket_launches: Mapped[list['RocketLaunch']] = relationship(
        cascade='all, delete-orphan', back_populates='rocket')

    def __repr__(self):
        return f"Rocket({self.id},{self.name})"


class LaunchSite(db.Model, TimestampMixin):
    __tablename__ = 'launch_sites'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    location: Mapped[str] = mapped_column(String(256))

    rocket_launches: Mapped[list['RocketLaunch']] = relationship(
        cascade='all, delete-orphan', back_populates='launch_site')

    def __repr__(self):
        return f"LaunchSite({self.id},{self.name})"
