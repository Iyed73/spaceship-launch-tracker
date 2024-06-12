from typing import Optional
from sqlalchemy import func,  String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship, WriteOnlyMapped
from app import db
from datetime import datetime, timezone
from uuid import UUID, uuid4


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=lambda: datetime.now(timezone.utc))


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
