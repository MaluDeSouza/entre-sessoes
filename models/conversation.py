from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class Conversation(Base):

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    started_at: Mapped[datetime]

    ended_at: Mapped[datetime | None]

    title: Mapped[str] = mapped_column(
        String(200)
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )