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
from app.features.watchlists.models import WatchlistAlert
from app.features.reports.models import Report

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
    DashboardIntelligenceSnapshotResponse,
    DashboardHighSeverityIntelligenceResponse,
    DashboardIocDistributionResponse,
    DashboardFeedContributionResponse,
    DashboardInvestigationSummaryResponse,
    TrendMetric,
    IocDistribution,
    FeedContribution,
    Insight,
    DashboardIntelligenceHighlightsResponse,
    PriorityQueueItem,
    DashboardPriorityQueueResponse,
    DashboardInvestigationHealthResponse,
    WatchlistActivity,
    DashboardWatchlistActivityResponse,
    RecentIntelligenceItem,
    DashboardGeospatialResponse,
    GeospatialCountryCount,
    DashboardSupplyChainResponse,
    SupplierThreatCount
)
from app.features.search.schemas import EntitySummary, IndicatorSummary
import uuid
from app.features.watchlists.models import Watchlist


class DashboardService:
    @staticmethod
    def get_overview(db: Session) -> DashboardOverviewResponse:
        total_indicators = db.query(func.count(Indicator.id)).scalar() or 0
        
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        new_indicators_24h = db.query(func.count(Indicator.id))\
            .filter(Indicator.created_at >= one_day_ago).scalar() or 0
            
        active_feeds = db.query(func.count(Feed.id))\
            .filter(Feed.enabled == True, Feed.status == FeedStatus.ACTIVE.value).scalar() or 0
            
        total_feeds = db.query(func.count(Feed.id))\
            .filter(Feed.enabled == True).scalar() or 0
        error_feeds = db.query(func.count(Feed.id))\
            .filter(Feed.enabled == True, Feed.status == FeedStatus.ERROR.value).scalar() or 0
            
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
    def _compute_trend(db: Session, model, current_start: datetime, prev_start: datetime) -> TrendMetric:
        current_count = db.query(func.count(model.id)).filter(model.created_at >= current_start).scalar() or 0
        prev_count = db.query(func.count(model.id)).filter(model.created_at >= prev_start, model.created_at < current_start).scalar() or 0
        if current_count > prev_count:
            trend = "up"
        elif current_count < prev_count:
            trend = "down"
        else:
            trend = "flat"
        return TrendMetric(count=current_count, trend=trend)

    @staticmethod
    def get_intelligence_snapshot(db: Session) -> DashboardIntelligenceSnapshotResponse:
        current_start = datetime.now(timezone.utc) - timedelta(days=1)
        prev_start = datetime.now(timezone.utc) - timedelta(days=2)
        
        new_indicators = DashboardService._compute_trend(db, Indicator, current_start, prev_start)
        new_threat_actors = DashboardService._compute_trend(db, ThreatActor, current_start, prev_start)
        new_malware = DashboardService._compute_trend(db, Malware, current_start, prev_start)
        new_campaigns = DashboardService._compute_trend(db, Campaign, current_start, prev_start)
        new_reports = DashboardService._compute_trend(db, Report, current_start, prev_start)
        
        # Open investigations
        current_open = db.query(func.count(Investigation.id)).filter(Investigation.status == InvestigationStatus.OPEN.value).scalar() or 0
        open_inv_trend = TrendMetric(count=current_open, trend="flat")

        return DashboardIntelligenceSnapshotResponse(
            new_indicators=new_indicators,
            new_threat_actors=new_threat_actors,
            new_malware=new_malware,
            new_campaigns=new_campaigns,
            new_reports=new_reports,
            open_investigations=open_inv_trend
        )

    @staticmethod
    def get_threat_activity(db: Session, days: int = 30) -> DashboardThreatActivityResponse:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        daily_counts_raw = db.query(
            func.date(Indicator.created_at).label('date'),
            func.count(Indicator.id).label('count')
        ).filter(Indicator.created_at >= start_date)\
         .group_by(func.date(Indicator.created_at))\
         .order_by(func.date(Indicator.created_at)).all()
         
        indicators_by_day = [DailyCount(date=str(row.date), count=row.count) for row in daily_counts_raw]
        
        def get_top_entities(assoc_table, entity_model, fk_col_name: str, limit: int = 5):
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
            
        active_watchlist_matches = db.query(WatchlistAlert).count()
        
        return DashboardOrganizationResponse(
            high_risk_asset_matches=high_risk_matches,
            supplier_threats=supplier_threats,
            automotive_threats=automotive_threats,
            active_watchlist_matches=active_watchlist_matches
        )

    @staticmethod
    def get_feed_status(db: Session) -> DashboardFeedStatusResponse:
        feed_stats = db.query(
            FeedRun.feed_id,
            func.count(FeedRun.id).label('total_runs'),
            func.sum(case((FeedRun.status == FeedRunStatus.FAILED.value, 1), else_=0)).label('failed_runs'),
            func.avg(FeedRun.duration).label('average_run_duration')
        ).group_by(FeedRun.feed_id).subquery()
        
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
        ).filter(Feed.enabled == True)\
         .outerjoin(feed_stats, Feed.id == feed_stats.c.feed_id)\
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
    def get_recent_intelligence(
        db: Session, 
        skip: int = 0, 
        limit: int = 50, 
        sort_by: str = 'created_at', 
        order: str = 'desc', 
        type_filter: str | None = None
    ) -> DashboardRecentIntelligenceResponse:
        query = db.query(Indicator)
        
        if type_filter:
            query = query.filter(Indicator.type == type_filter)
            
        total_count = query.count()
        
        sort_col = getattr(Indicator, sort_by, Indicator.created_at)
        if order == 'desc':
            sort_col = sort_col.desc()
            
        inds = query.order_by(sort_col).offset(skip).limit(limit).all()
        
        items = []
        for i in inds:
            items.append(RecentIntelligenceItem(
                id=i.id,
                type=i.type,
                value=i.value,
                severity=i.severity or 'unknown',
                confidence=i.confidence or 0,
                risk_score=i.risk_score or 0,
                source="System",
                created_at=i.created_at,
                tags=[]
            ))
            
        page = (skip // limit) + 1 if limit > 0 else 1
        has_next = (skip + limit) < total_count
        
        return DashboardRecentIntelligenceResponse(
            items=items,
            total_count=total_count,
            page=page,
            has_next_page=has_next
        )

    @staticmethod
    def get_priority_alerts(
        db: Session,
        limit: int = 5,
        min_score: int = 50
    ) -> DashboardRecentIntelligenceResponse:
        inds = db.query(Indicator)\
            .filter(Indicator.risk_score >= min_score)\
            .order_by(Indicator.risk_score.desc(), Indicator.created_at.desc())\
            .limit(limit).all()
            
        items = []
        for i in inds:
            items.append(RecentIntelligenceItem(
                id=i.id,
                type=i.type,
                value=i.value,
                severity=i.severity or 'unknown',
                confidence=i.confidence or 0,
                risk_score=i.risk_score or 0,
                source="System",
                created_at=i.created_at,
                tags=[]
            ))
            
        return DashboardRecentIntelligenceResponse(
            items=items,
            total_count=len(items),
            page=1,
            has_next_page=False
        )

    @staticmethod
    def get_high_severity_intelligence(db: Session, limit: int = 10) -> DashboardHighSeverityIntelligenceResponse:
        inds = db.query(Indicator)\
            .filter(Indicator.severity.in_(["high", "critical"]))\
            .order_by(Indicator.created_at.desc())\
            .limit(limit).all()
        return DashboardHighSeverityIntelligenceResponse(
            indicators=[IndicatorSummary.model_validate(i) for i in inds]
        )

    @staticmethod
    def get_ioc_distribution(db: Session) -> DashboardIocDistributionResponse:
        dist_raw = db.query(Indicator.type, func.count(Indicator.id).label('count'))\
            .group_by(Indicator.type)\
            .order_by(desc('count')).all()
        
        distribution = [IocDistribution(type=row.type, count=row.count) for row in dist_raw]
        return DashboardIocDistributionResponse(distribution=distribution)

    @staticmethod
    def get_feed_contribution(db: Session) -> DashboardFeedContributionResponse:
        feeds_raw = db.query(Feed.name, Feed.records_imported)\
            .filter(Feed.records_imported > 0)\
            .order_by(desc(Feed.records_imported))\
            .all()
        contribution = [FeedContribution(feed_name=r.name, count=r.records_imported) for r in feeds_raw]
        return DashboardFeedContributionResponse(contribution=contribution)

    @staticmethod
    def get_investigation_summary(db: Session) -> DashboardInvestigationSummaryResponse:
        open_count = db.query(func.count(Investigation.id)).filter(Investigation.status == "open").scalar() or 0
        high_priority = db.query(func.count(Investigation.id)).filter(Investigation.status == "open", Investigation.priority.in_(["high", "critical"])).scalar() or 0
        closed_count = db.query(func.count(Investigation.id)).filter(Investigation.status == "closed").scalar() or 0
        
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recently_updated = db.query(func.count(Investigation.id)).filter(Investigation.updated_at >= one_week_ago).scalar() or 0
        
        return DashboardInvestigationSummaryResponse(
            open=open_count,
            high_priority=high_priority,
            closed=closed_count,
            recently_updated=recently_updated
        )

    @staticmethod
    def get_intelligence_highlights(db: Session) -> DashboardIntelligenceHighlightsResponse:
        current_start = datetime.now(timezone.utc) - timedelta(days=1)
        prev_start = datetime.now(timezone.utc) - timedelta(days=2)
        
        insights = []
        
        current_crit_ioc = db.query(func.count(Indicator.id)).filter(Indicator.created_at >= current_start, Indicator.severity == 'critical').scalar() or 0
        prev_crit_ioc = db.query(func.count(Indicator.id)).filter(Indicator.created_at >= prev_start, Indicator.created_at < current_start, Indicator.severity == 'critical').scalar() or 0
        
        if current_crit_ioc > prev_crit_ioc * 1.5 and current_crit_ioc >= 5:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type='spike',
                title="Spike in Critical Indicators",
                description=f"Detected {current_crit_ioc} critical indicators in the last 24h, compared to {prev_crit_ioc} previously.",
                severity="critical",
                metric=current_crit_ioc,
                trend="up",
                entity_type="indicator",
                timestamp=datetime.now(timezone.utc)
            ))
            
        wl_hits = db.query(func.count(WatchlistAlert.id)).filter(WatchlistAlert.created_at >= current_start).scalar() or 0
        if wl_hits > 0:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type='watchlist_hit',
                title="New Watchlist Matches",
                description=f"There are {wl_hits} new watchlist matches in the last 24 hours.",
                severity="high",
                metric=wl_hits,
                trend="up",
                entity_type="watchlist_match",
                timestamp=datetime.now(timezone.utc)
            ))
            
        unassigned_high_inv = db.query(func.count(Investigation.id)).filter(Investigation.status == 'open', Investigation.priority.in_(['high', 'critical'])).scalar() or 0
        if unassigned_high_inv > 0:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type='investigation',
                title="High Priority Investigations",
                description=f"{unassigned_high_inv} high priority investigations are currently open.",
                severity="high",
                metric=unassigned_high_inv,
                trend="flat",
                entity_type="investigation",
                timestamp=datetime.now(timezone.utc)
            ))
            
        if not insights:
            insights.append(Insight(
                id=str(uuid.uuid4()),
                type='info',
                title="Operations Normal",
                description="No significant operational spikes or critical alerts in the last 24 hours.",
                severity="low",
                timestamp=datetime.now(timezone.utc)
            ))
            
        return DashboardIntelligenceHighlightsResponse(insights=insights)

    @staticmethod
    def get_priority_queue(db: Session) -> DashboardPriorityQueueResponse:
        items = []
        
        invs = db.query(Investigation).filter(Investigation.status == 'open', Investigation.priority.in_(['high', 'critical'])).order_by(Investigation.updated_at.desc()).limit(5).all()
        for i in invs:
            items.append(PriorityQueueItem(
                id=str(i.id),
                icon="briefcase",
                item_type="investigation",
                title=str(i.title or 'Unknown'),
                subtitle=f"Status: {(i.status or 'open').upper()} | Priority: {(i.priority or 'high').upper()}",
                priority=str(i.priority or 'high'),
                action="Open",
                timestamp=i.updated_at or i.created_at or datetime.now(timezone.utc),
                reference_id=str(i.id)
            ))
            
        matches = db.query(WatchlistAlert).order_by(WatchlistAlert.created_at.desc()).limit(5).all()
        for m in matches:
            items.append(PriorityQueueItem(
                id=str(m.id),
                icon="eye",
                item_type="watchlist_match",
                title=f"Watchlist Hit: Indicator {m.indicator_id}",
                subtitle=f"Reason: {m.matched_rule or 'Matched criteria'}",
                priority="high",
                action="Review",
                timestamp=m.created_at or datetime.now(timezone.utc),
                reference_id=str(m.indicator_id) if m.indicator_id else None
            ))
            
        crit_inds = db.query(Indicator).filter(Indicator.severity == 'critical').order_by(Indicator.created_at.desc()).limit(5).all()
        for ind in crit_inds:
            items.append(PriorityQueueItem(
                id=str(ind.id),
                icon="target",
                item_type="indicator",
                title=str(ind.value or 'Unknown'),
                subtitle=f"Type: {(ind.type or 'unknown').upper()} | Confidence: {ind.confidence or 0}%",
                priority="critical",
                action="Triage",
                timestamp=ind.created_at or datetime.now(timezone.utc),
                reference_id=str(ind.id)
            ))
            
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return DashboardPriorityQueueResponse(items=items[:10])

    @staticmethod
    def get_investigation_health(db: Session) -> DashboardInvestigationHealthResponse:
        open_count = db.query(func.count(Investigation.id)).filter(Investigation.status == 'open').scalar() or 0
        high_priority = db.query(func.count(Investigation.id)).filter(Investigation.status == 'open', Investigation.priority.in_(['high', 'critical'])).scalar() or 0
        
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        overdue = db.query(func.count(Investigation.id)).filter(Investigation.status == 'open', Investigation.updated_at < seven_days_ago).scalar() or 0
        
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        updated_today = db.query(func.count(Investigation.id)).filter(Investigation.updated_at >= today_start).scalar() or 0
        
        return DashboardInvestigationHealthResponse(
            open=open_count,
            high_priority=high_priority,
            overdue=overdue,
            updated_today=updated_today
        )

    @staticmethod
    def get_watchlist_activity(db: Session) -> DashboardWatchlistActivityResponse:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        hits = db.query(
            Watchlist.id,
            Watchlist.name,
            func.count(WatchlistAlert.id).label('hit_count')
        ).join(WatchlistAlert, Watchlist.id == WatchlistAlert.watchlist_id)\
         .filter(WatchlistAlert.created_at >= today_start)\
         .group_by(Watchlist.id, Watchlist.name)\
         .order_by(desc('hit_count'))\
         .limit(5).all()
         
        activities = [WatchlistActivity(watchlist_id=h.id, watchlist_name=h.name, hits_today=h.hit_count) for h in hits]
        return DashboardWatchlistActivityResponse(activities=activities)

    @staticmethod
    def get_geospatial_threats(db: Session, days: int = 7) -> DashboardGeospatialResponse:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # We use ThreatActor's country or a mock mapping for IPs if no country is directly on the Indicator
        # For this widget, we'll query indicators that have an associated Threat Actor with a country
        # or we will return a hardcoded distribution for demonstration until MaxMind GeoIP is integrated.
        
        countries_raw = db.query(
            ThreatActor.country,
            func.count(indicator_threat_actor.c.indicator_id).label('count')
        ).join(indicator_threat_actor, ThreatActor.id == indicator_threat_actor.c.threat_actor_id)\
         .join(Indicator, Indicator.id == indicator_threat_actor.c.indicator_id)\
         .filter(ThreatActor.country != None, Indicator.created_at >= start_date)\
         .group_by(ThreatActor.country)\
         .order_by(desc('count'))\
         .limit(20).all()
         
        countries = [GeospatialCountryCount(country=r.country, count=r.count) for r in countries_raw]
        
        return DashboardGeospatialResponse(countries=countries)

    @staticmethod
    def get_supply_chain_matrix(db: Session, days: int = 30) -> DashboardSupplyChainResponse:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        suppliers_raw = db.query(
            Asset.id,
            Asset.name,
            func.count(indicator_asset.c.indicator_id).label('count')
        ).join(indicator_asset, Asset.id == indicator_asset.c.asset_id)\
         .join(Indicator, Indicator.id == indicator_asset.c.indicator_id)\
         .filter(Asset.type == AssetType.SUPPLIER.value, Indicator.created_at >= start_date)\
         .group_by(Asset.id, Asset.name)\
         .order_by(desc('count'))\
         .limit(20).all()
         
        suppliers = [SupplierThreatCount(supplier_id=r.id, supplier_name=r.name, threat_count=r.count) for r in suppliers_raw]
        return DashboardSupplyChainResponse(suppliers=suppliers)
