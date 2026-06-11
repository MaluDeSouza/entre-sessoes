from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from database.base import Base


class Keyword(Base):

    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("emotional_analysis.id"),
        nullable=False
    )

    keyword: Mapped[str] = mapped_column(
        String(100)
    )