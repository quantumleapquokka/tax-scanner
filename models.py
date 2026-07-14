from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TaxReturn(Base):
    """
    Represents a reviewed and accepted Form 1040 record stored in the
    application's SQLite database.
    """

    __tablename__ = "tax_returns"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    taxpayer_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    filing_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    wages: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    adjusted_gross_income: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    total_tax: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    refund_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="accepted",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )