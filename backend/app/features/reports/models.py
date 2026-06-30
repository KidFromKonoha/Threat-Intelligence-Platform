"""Report and Comment ORM models.

Report represents a written intelligence report that may reference any entity.
Comment represents analyst collaboration notes attached to any entity.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import CommentEntityType
from app.db.mixins import TimestampMixin
from app.db.session import Base


class Report(Base, TimestampMixin):
    """Represents a written threat intelligence report."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    title: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Free-form author identifier; auth is a future phase.
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    # List of external URLs or citation objects.
    references: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    indicators: Mapped[list] = relationship(
        "Indicator",
        secondary="indicator_report",
        back_populates="reports",
    )
    threat_actors: Mapped[list] = relationship(
        "ThreatActor",
        secondary="threat_actor_report",
        back_populates="reports",
    )
    malware: Mapped[list] = relationship(
        "Malware",
        secondary="malware_report",
        back_populates="reports",
    )
    campaigns: Mapped[list] = relationship(
        "Campaign",
        secondary="campaign_report",
        back_populates="reports",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="report",
        cascade="all, delete-orphan",
        foreign_keys="Comment.report_id",
    )

    def __repr__(self) -> str:
        return f"<Report id={self.id!r} title={self.title!r}>"


class Comment(Base, TimestampMixin):
    """Represents an analyst collaboration comment on any entity.

    A comment is linked to exactly one parent entity.  Both FKs are nullable;
    only one will be populated depending on which entity the comment belongs to.
    This avoids a polymorphic association table while keeping the schema simple
    for Phase 2.  Future phases may introduce a generic entity-reference table.
    """

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    entity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="CommentEntityType enum stored as string",
    )
    # FK to investigation (nullable — only set when entity_type == 'investigation')
    investigation_id: Mapped[str | None] = mapped_column(
        Text,
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # FK to report (nullable — only set when entity_type == 'report')
    report_id: Mapped[str | None] = mapped_column(
        Text,
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # Free-form author identifier; auth is a future phase.
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    investigation: Mapped["Investigation | None"] = relationship(  # type: ignore[name-defined]
        "Investigation",
        back_populates="comments",
        foreign_keys=[investigation_id],
    )
    report: Mapped["Report | None"] = relationship(
        "Report",
        back_populates="comments",
        foreign_keys=[report_id],
    )

    def __repr__(self) -> str:
        return f"<Comment id={self.id!r} entity_type={self.entity_type!r} author={self.author!r}>"
