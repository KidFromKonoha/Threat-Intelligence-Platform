"""SQLAlchemy association tables for all many-to-many relationships.

All join tables live here in one place to avoid circular imports between
feature model modules and to make the relationship graph easy to review.
Each table uses UUID foreign keys matching the primary keys of the related
entities.  No ORM classes are defined here — only plain Table objects.
"""

from sqlalchemy import Column, ForeignKey, Table, Text

from app.db.session import Base

# ---------------------------------------------------------------------------
# Indicator associations
# ---------------------------------------------------------------------------

indicator_threat_actor = Table(
    "indicator_threat_actor",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
)

indicator_malware = Table(
    "indicator_malware",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
)

indicator_campaign = Table(
    "indicator_campaign",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
)

indicator_mitre_technique = Table(
    "indicator_mitre_technique",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("technique_id", Text, ForeignKey("mitre_techniques.id", ondelete="CASCADE"), primary_key=True),
)

indicator_asset = Table(
    "indicator_asset",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("asset_id", Text, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
)

indicator_report = Table(
    "indicator_report",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("report_id", Text, ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
)

indicator_feed = Table(
    "indicator_feed",
    Base.metadata,
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("feed_id", Text, ForeignKey("feeds.id", ondelete="CASCADE"), primary_key=True),
)

# ---------------------------------------------------------------------------
# Threat Actor associations
# ---------------------------------------------------------------------------

threat_actor_malware = Table(
    "threat_actor_malware",
    Base.metadata,
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
)

threat_actor_campaign = Table(
    "threat_actor_campaign",
    Base.metadata,
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
)

threat_actor_mitre_technique = Table(
    "threat_actor_mitre_technique",
    Base.metadata,
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
    Column("technique_id", Text, ForeignKey("mitre_techniques.id", ondelete="CASCADE"), primary_key=True),
)

threat_actor_report = Table(
    "threat_actor_report",
    Base.metadata,
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
    Column("report_id", Text, ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
)

# ---------------------------------------------------------------------------
# Malware associations
# ---------------------------------------------------------------------------

malware_campaign = Table(
    "malware_campaign",
    Base.metadata,
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
)

malware_mitre_technique = Table(
    "malware_mitre_technique",
    Base.metadata,
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
    Column("technique_id", Text, ForeignKey("mitre_techniques.id", ondelete="CASCADE"), primary_key=True),
)

malware_report = Table(
    "malware_report",
    Base.metadata,
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
    Column("report_id", Text, ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
)

# ---------------------------------------------------------------------------
# Campaign associations
# ---------------------------------------------------------------------------

campaign_vulnerability = Table(
    "campaign_vulnerability",
    Base.metadata,
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
    Column("vulnerability_id", Text, ForeignKey("vulnerabilities.id", ondelete="CASCADE"), primary_key=True),
)

campaign_mitre_technique = Table(
    "campaign_mitre_technique",
    Base.metadata,
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
    Column("technique_id", Text, ForeignKey("mitre_techniques.id", ondelete="CASCADE"), primary_key=True),
)

campaign_report = Table(
    "campaign_report",
    Base.metadata,
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
    Column("report_id", Text, ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
)

# ---------------------------------------------------------------------------
# Vulnerability associations
# ---------------------------------------------------------------------------

vulnerability_threat_actor = Table(
    "vulnerability_threat_actor",
    Base.metadata,
    Column("vulnerability_id", Text, ForeignKey("vulnerabilities.id", ondelete="CASCADE"), primary_key=True),
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
)

vulnerability_malware = Table(
    "vulnerability_malware",
    Base.metadata,
    Column("vulnerability_id", Text, ForeignKey("vulnerabilities.id", ondelete="CASCADE"), primary_key=True),
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
)

# ---------------------------------------------------------------------------
# Investigation associations
# ---------------------------------------------------------------------------

investigation_indicator = Table(
    "investigation_indicator",
    Base.metadata,
    Column("investigation_id", Text, ForeignKey("investigations.id", ondelete="CASCADE"), primary_key=True),
    Column("indicator_id", Text, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
)

investigation_threat_actor = Table(
    "investigation_threat_actor",
    Base.metadata,
    Column("investigation_id", Text, ForeignKey("investigations.id", ondelete="CASCADE"), primary_key=True),
    Column("threat_actor_id", Text, ForeignKey("threat_actors.id", ondelete="CASCADE"), primary_key=True),
)

investigation_malware = Table(
    "investigation_malware",
    Base.metadata,
    Column("investigation_id", Text, ForeignKey("investigations.id", ondelete="CASCADE"), primary_key=True),
    Column("malware_id", Text, ForeignKey("malware.id", ondelete="CASCADE"), primary_key=True),
)

investigation_campaign = Table(
    "investigation_campaign",
    Base.metadata,
    Column("investigation_id", Text, ForeignKey("investigations.id", ondelete="CASCADE"), primary_key=True),
    Column("campaign_id", Text, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
)

investigation_asset = Table(
    "investigation_asset",
    Base.metadata,
    Column("investigation_id", Text, ForeignKey("investigations.id", ondelete="CASCADE"), primary_key=True),
    Column("asset_id", Text, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
)
