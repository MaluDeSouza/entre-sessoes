from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class EmotionalAnalysis(Base):

    __tablename__ = "emotional_analysis"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False
    )

    main_theme: Mapped[str] = mapped_column(
        String(100)
    )

    sub_theme: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    intensity: Mapped[float]

    analysis_json: Mapped[dict] = mapped_column(
        JSONB
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )