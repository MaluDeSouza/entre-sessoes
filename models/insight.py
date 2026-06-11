from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class Insight(Base):

    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    text: Mapped[str] = mapped_column(
        Text
    )

    period: Mapped[str] = mapped_column(
        String(30)
    )