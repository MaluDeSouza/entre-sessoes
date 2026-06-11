from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class Emotion(Base):

    __tablename__ = "emotions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("emotional_analysis.id"),
        nullable=False
    )

    emotion: Mapped[str] = mapped_column(
        String(50)
    )

    score: Mapped[float]