"""Feed and FeedRun ORM models.

Feed represents an external threat intelligence provider.
FeedRun represents one scheduled execution of a feed collector.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import FeedRunStatus, FeedStatus, FeedType
from app.db.mixins import TimestampMixin
from app.db.session import Base


class Feed(Base, TimestampMixin):
    """Represents an external threat intelligence feed provider."""

    __tablename__ = "feeds"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=FeedType.OPEN_SOURCE.value,
        comment="FeedType enum stored as string",
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Cron expression or interval descriptor, e.g. "0 */6 * * *"
    schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Stored as JSON to support arbitrary auth schemes (API key, OAuth, etc.)
    authentication: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Requests per minute; None means unlimited.
    rate_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    last_success: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_failure: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    records_imported: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=FeedStatus.ACTIVE.value,
        index=True,
        comment="FeedStatus enum stored as string",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    runs: Mapped[list["FeedRun"]] = relationship(
        "FeedRun", back_populates="feed", cascade="all, delete-orphan"
    )
    indicators: Mapped[list] = relationship(
        "Indicator",
        secondary="indicator_feed",
        back_populates="feeds",
    )

    def __repr__(self) -> str:
        return f"<Feed id={self.id!r} name={self.name!r} status={self.status!r}>"


class FeedRun(Base):
    """Records one execution of a Feed collector.

    FeedRun does not use TimestampMixin because start_time / end_time
    already capture the full lifecycle of the run.
    """

    __tablename__ = "feed_runs"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    feed_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("feeds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Duration in seconds (computed and stored on completion for fast reporting).
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=FeedRunStatus.RUNNING.value,
        index=True,
        comment="FeedRunStatus enum stored as string",
    )
    records_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_added: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Structured error list; None means no errors.
    errors: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    feed: Mapped["Feed"] = relationship("Feed", back_populates="runs")

    def __repr__(self) -> str:
        return f"<FeedRun id={self.id!r} feed_id={self.feed_id!r} status={self.status!r}>"
