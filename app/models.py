from typing import Optional
from sqlalchemy import func,  String, Integer, ForeignKey, Table, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship, WriteOnlyMapped
from app import db
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))


class CreatedByMixin:
    @declared_attr
    def creator_id(cls):
        return Column(ForeignKey('users.id'))

    @declared_attr
    def creator(cls):
        return relationship('User')


class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    password_hash = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(128), default='spectator')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'{self.role}({self.id.hex}, "{self.username}", {self.email})'


@login.user_loader
def load_user(id):
    return db.session.get(User, UUID(id))


class Launch(db.Model, TimestampMixin, CreatedByMixin):
    __tablename__ = 'launches'

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    mission: Mapped[String] = mapped_column(String(128), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    launch_timestamp: Mapped[datetime]
    spaceship_id: Mapped[int] = mapped_column(ForeignKey('spaceships.id'), index=True)
    launch_site_id: Mapped[int] = mapped_column(ForeignKey('launch_sites.id'), index=True)

    spaceship: Mapped['Spaceship'] = relationship(
        lazy='joined', back_populates='launches'
    )

    launch_site: Mapped['LaunchSite'] = relationship(
        lazy='joined', back_populates='launches'
    )

    def __repr__(self):
        return f"Launch({self.id.hex},{self.mission})"


class Spaceship(db.Model, TimestampMixin, CreatedByMixin):
    __tablename__ = 'spaceships'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    height: Mapped[float]
    mass: Mapped[float]
    payload_capacity: Mapped[float]
    thrust_at_liftoff: Mapped[float]

    launches: Mapped[list['Launch']] = relationship(
        cascade='all, delete-orphan', back_populates='spaceship')

    def __repr__(self):
        return f"Spaceship({self.id},{self.name})"


class LaunchSite(db.Model, TimestampMixin, CreatedByMixin):
    __tablename__ = 'launch_sites'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    location: Mapped[str] = mapped_column(String(256))

    launches: Mapped[list['Launch']] = relationship(
        cascade='all, delete-orphan', back_populates='launch_site')

    def __repr__(self):
        return f"LaunchSite({self.id},{self.name})"
