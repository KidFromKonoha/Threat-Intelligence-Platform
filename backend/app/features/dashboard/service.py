"""Dashboard Service for aggregating threat intelligence metrics."""

from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, desc, case
from sqlalchemy.orm import Session

from app.db.enums import (
    AssetCriticality,
    AssetType,
    FeedRunStatus,
    FeedStatus,
    InvestigationStatus,
)
from app.db.associations import (
    indicator_asset,
    indicator_campaign,
    indicator_malware,
    indicator_threat_actor,
    indicator_mitre_technique,
)
from app.features.assets.models import Asset
from app.features.campaigns.models import Campaign
from app.features.feeds.models import Feed, FeedRun
from app.features.indicators.models import Indicator
from app.features.investigations.models import Investigation
from app.features.malware.models import Malware
from app.features.mitre.models import MITRETechnique
from app.features.threat_actors.models import ThreatActor
from app.features.vulnerabilities.models import Vulnerability

from app.features.dashboard.schemas import (
    DashboardOverviewResponse,
    FeedHealthScore,
    DashboardThreatActivityResponse,
    DailyCount,
    TopEntity,
    DashboardOrganizationResponse,
    DashboardFeedStatusResponse,
    FeedStatusDetail,
    DashboardRecentIntelligenceResponse,
)
from app.features.search.schemas import EntitySummary, IndicatorSummary


class DashboardService:
    @staticmethod
    def get_overview(db: Session) -> DashboardOverviewResponse:
        total_indicators = db.query(func.count(Indicator.id)).scalar() or 0
        
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        new_indicators_24h = db.query(func.count(Indicator.id))\
            .filter(Indicator.created_at >= one_day_ago).scalar() or 0
            
        active_feeds = db.query(func.count(Feed.id))\
            .filter(Feed.status == FeedStatus.ACTIVE.value).scalar() or 0
            
        total_feeds = db.query(func.count(Feed.id)).scalar() or 0
        error_feeds = db.query(func.count(Feed.id))\
            .filter(Feed.status == FeedStatus.ERROR.value).scalar() or 0
            
        health_percentage = (active_feeds / total_feeds * 100.0) if total_feeds > 0 else 0.0
        feed_health = FeedHealthScore(
            healthy_feeds=active_feeds,
            error_feeds=error_feeds,
            total_active_feeds=total_feeds,
            health_percentage=round(health_percentage, 2)
        )
        
        open_investigations = db.query(func.count(Investigation.id))\
            .filter(Investigation.status == InvestigationStatus.OPEN.value).scalar() or 0
            
        return DashboardOverviewResponse(
            total_indicators=total_indicators,
            new_indicators_24h=new_indicators_24h,
            active_feeds=active_feeds,
            feed_health=feed_health,
            open_investigations=open_investigations
        )

    @staticmethod
    def get_threat_activity(db: Session) -> DashboardThreatActivityResponse:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Indicators by day
        # In SQLite func.date() returns a string. In Postgres, func.date() or cast to Date.
        # We'll use cast(Indicator.created_at, sa.Date) or func.date. Since this is Postgres, func.date works.
        daily_counts_raw = db.query(
            func.date(Indicator.created_at).label('date'),
            func.count(Indicator.id).label('count')
        ).filter(Indicator.created_at >= thirty_days_ago)\
         .group_by(func.date(Indicator.created_at))\
         .order_by(func.date(Indicator.created_at)).all()
         
        indicators_by_day = [DailyCount(date=str(row.date), count=row.count) for row in daily_counts_raw]
        
        # Helper to get top entities
        def get_top_entities(assoc_table, entity_model, fk_col_name: str, limit: int = 5):
            # e.g. indicator_threat_actor, ThreatActor, "threat_actor_id"
            fk_col = getattr(assoc_table.c, fk_col_name)
            rows = db.query(
                entity_model.id,
                entity_model.name,
                func.count(assoc_table.c.indicator_id).label('count')
            ).join(assoc_table, entity_model.id == fk_col)\
             .group_by(entity_model.id, entity_model.name)\
             .order_by(desc('count'))\
             .limit(limit).all()
            return [TopEntity(id=r.id, name=r.name, count=r.count) for r in rows]

        top_threat_actors = get_top_entities(indicator_threat_actor, ThreatActor, "threat_actor_id")
        top_malware = get_top_entities(indicator_malware, Malware, "malware_id")
        top_campaigns = get_top_entities(indicator_campaign, Campaign, "campaign_id")
        top_mitre = get_top_entities(indicator_mitre_technique, MITRETechnique, "technique_id")
        
        # top_countries (based on ThreatActor country)
        countries_raw = db.query(
            ThreatActor.country,
            func.count(indicator_threat_actor.c.indicator_id).label('count')
        ).join(indicator_threat_actor, ThreatActor.id == indicator_threat_actor.c.threat_actor_id)\
         .filter(ThreatActor.country != None)\
         .group_by(ThreatActor.country)\
         .order_by(desc('count'))\
         .limit(5).all()
         
        top_countries = [TopEntity(id=r.country, name=r.country, count=r.count) for r in countries_raw]
        
        return DashboardThreatActivityResponse(
            indicators_by_day=indicators_by_day,
            top_threat_actors=top_threat_actors,
            top_malware_families=top_malware,
            top_campaigns=top_campaigns,
            top_countries=top_countries,
            top_mitre_techniques=top_mitre
        )

    @staticmethod
    def get_organization(db: Session) -> DashboardOrganizationResponse:
        high_risk_matches = db.query(func.count(indicator_asset.c.indicator_id))\
            .join(Asset, Asset.id == indicator_asset.c.asset_id)\
            .filter(Asset.criticality.in_([AssetCriticality.HIGH.value, AssetCriticality.CRITICAL.value]))\
            .scalar() or 0
            
        supplier_threats = db.query(func.count(indicator_asset.c.indicator_id))\
            .join(Asset, Asset.id == indicator_asset.c.asset_id)\
            .filter(Asset.type == AssetType.SUPPLIER.value)\
            .scalar() or 0
            
        automotive_threats = db.query(func.count(indicator_asset.c.indicator_id))\
            .join(Asset, Asset.id == indicator_asset.c.asset_id)\
            .filter(Asset.type == AssetType.VEHICLE_PLATFORM.value)\
            .scalar() or 0
            
        # Watchlists are not implemented (Phase 9 instructions say "Do not implement Watchlists")
        active_watchlist_matches = 0
        
        return DashboardOrganizationResponse(
            high_risk_asset_matches=high_risk_matches,
            supplier_threats=supplier_threats,
            automotive_threats=automotive_threats,
            active_watchlist_matches=active_watchlist_matches
        )

    @staticmethod
    def get_feed_status(db: Session) -> DashboardFeedStatusResponse:
        # We need feed stats from FeedRun.
        # total_runs, failed_runs, average_run_duration
        feed_stats = db.query(
            FeedRun.feed_id,
            func.count(FeedRun.id).label('total_runs'),
            func.sum(case((FeedRun.status == FeedRunStatus.FAILED.value, 1), else_=0)).label('failed_runs'),
            func.avg(FeedRun.duration).label('average_run_duration')
        ).group_by(FeedRun.feed_id).subquery()
        
        # For last_run_duration, use DISTINCT ON in Postgres
        last_runs = db.query(FeedRun.feed_id, FeedRun.duration)\
            .distinct(FeedRun.feed_id)\
            .order_by(FeedRun.feed_id, FeedRun.start_time.desc())\
            .subquery()
            
        feeds_raw = db.query(
            Feed.id, Feed.name, Feed.status, Feed.last_success, Feed.last_failure, Feed.records_imported,
            feed_stats.c.total_runs,
            feed_stats.c.failed_runs,
            feed_stats.c.average_run_duration,
            last_runs.c.duration.label('last_run_duration')
        ).outerjoin(feed_stats, Feed.id == feed_stats.c.feed_id)\
         .outerjoin(last_runs, Feed.id == last_runs.c.feed_id)\
         .all()
         
        feed_details = []
        for r in feeds_raw:
            feed_details.append(FeedStatusDetail(
                id=r.id,
                name=r.name,
                status=r.status,
                last_success=r.last_success,
                last_failure=r.last_failure,
                records_imported=r.records_imported,
                last_run_duration=r.last_run_duration,
                average_run_duration=r.average_run_duration,
                total_runs=r.total_runs or 0,
                failed_runs=r.failed_runs or 0
            ))
            
        return DashboardFeedStatusResponse(feeds=feed_details)

    @staticmethod
    def get_recent_intelligence(db: Session, limit: int = 5) -> DashboardRecentIntelligenceResponse:
        # Indicators
        inds = db.query(Indicator).order_by(Indicator.created_at.desc()).limit(limit).all()
        indicator_summaries = [IndicatorSummary.model_validate(i) for i in inds]
        
        # Campaigns
        camps = db.query(Campaign).order_by(Campaign.created_at.desc()).limit(limit).all()
        campaign_summaries = [EntitySummary(id=c.id, name=c.name, entity_type="campaign", description=c.description) for c in camps]
        
        # Malware
        mals = db.query(Malware).order_by(Malware.created_at.desc()).limit(limit).all()
        malware_summaries = [EntitySummary(id=m.id, name=m.name, entity_type="malware", description=m.description) for m in mals]
        
        # Threat Actors
        tas = db.query(ThreatActor).order_by(ThreatActor.created_at.desc()).limit(limit).all()
        ta_summaries = [EntitySummary(id=t.id, name=t.name, entity_type="threat_actor", description=t.description) for t in tas]
        
        # Vulnerabilities
        vulns = db.query(Vulnerability).order_by(Vulnerability.created_at.desc()).limit(limit).all()
        vuln_summaries = [EntitySummary(id=v.id, name=v.cve, entity_type="vulnerability", description=v.description) for v in vulns]
        
        return DashboardRecentIntelligenceResponse(
            indicators=indicator_summaries,
            campaigns=campaign_summaries,
            malware=malware_summaries,
            threat_actors=ta_summaries,
            vulnerabilities=vuln_summaries
        )
