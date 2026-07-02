"""ReportService.

Aggregates data for intelligence reports and generates export formats.
"""

from __future__ import annotations
import csv
import io
from datetime import datetime, timezone, timedelta
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from fpdf import FPDF

from app.features.dashboard.service import DashboardService
from app.features.investigations.models import Investigation
from app.features.vulnerabilities.models import Vulnerability
from app.features.reports.schemas import (
    ReportResponse,
    ReportPlatformOverview,
    ReportThreatIntelligence,
    ReportInvestigations,
    InvestigationStats,
    InvestigationSummary,
    ReportFeedStatistics,
    FeedStat,
    TopEntityStats,
)


class ReportService:
    @staticmethod
    def generate_report(db: Session, report_type: str) -> ReportResponse:
        """Generates the canonical JSON report model from existing services."""
        # 1. Platform Overview
        overview = DashboardService.get_overview(db)
        org = DashboardService.get_organization(db)
        
        platform_overview = ReportPlatformOverview(
            total_indicators=overview.total_indicators,
            new_indicators=overview.new_indicators_24h,
            active_feeds=overview.active_feeds,
            feed_health_percentage=overview.feed_health.health_percentage,
            open_investigations=overview.open_investigations,
            active_watchlist_matches=org.active_watchlist_matches,
        )

        # 2. Threat Intelligence
        threat_activity = DashboardService.get_threat_activity(db)
        
        # Top vulnerabilities by CVSS
        top_vulns_raw = db.query(Vulnerability).order_by(Vulnerability.cvss.desc().nulls_last()).limit(5).all()
        top_vulns = [TopEntityStats(name=r.cve, count=int(r.cvss or 0)) for r in top_vulns_raw]

        threat_intelligence = ReportThreatIntelligence(
            top_malware=[TopEntityStats(name=m.name, count=m.count) for m in threat_activity.top_malware_families],
            top_threat_actors=[TopEntityStats(name=t.name, count=t.count) for t in threat_activity.top_threat_actors],
            top_campaigns=[TopEntityStats(name=c.name, count=c.count) for c in threat_activity.top_campaigns],
            top_mitre_techniques=[TopEntityStats(name=m.name, count=m.count) for m in threat_activity.top_mitre_techniques],
            top_vulnerabilities=top_vulns,
            most_active_countries=[TopEntityStats(name=c.name, count=c.count) for c in threat_activity.top_countries],
        )

        # 3. Investigations
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        
        total_inv = db.query(func.count(Investigation.id)).scalar() or 0
        open_inv = db.query(func.count(Investigation.id)).filter(Investigation.status == "open").scalar() or 0
        closed_inv = db.query(func.count(Investigation.id)).filter(Investigation.status == "closed").scalar() or 0
        
        open_list = db.query(Investigation).filter(Investigation.status == "open").order_by(Investigation.created_at.desc()).limit(10).all()
        recent_created = db.query(Investigation).filter(Investigation.created_at >= thirty_days_ago).order_by(Investigation.created_at.desc()).limit(5).all()
        recent_closed = db.query(Investigation).filter(Investigation.closed_at >= thirty_days_ago).order_by(Investigation.closed_at.desc()).limit(5).all()
        
        def _to_summary(inv):
            return InvestigationSummary(
                id=inv.id, title=inv.title, status=inv.status, created_at=inv.created_at, closed_at=inv.closed_at
            )
            
        investigations = ReportInvestigations(
            open_investigations=[_to_summary(i) for i in open_list],
            recently_created=[_to_summary(i) for i in recent_created],
            recently_closed=[_to_summary(i) for i in recent_closed],
            statistics=InvestigationStats(total=total_inv, open=open_inv, closed=closed_inv),
        )

        # 4. Feed Statistics
        feed_status = DashboardService.get_feed_status(db)
        feeds = []
        for f in feed_status.feeds:
            feeds.append(FeedStat(
                name=f.name,
                status=f.status,
                total_imports=f.records_imported,
                failed_runs=f.failed_runs,
                average_runtime_seconds=f.average_run_duration or 0.0
            ))
            
        feed_stats = ReportFeedStatistics(feeds=feeds)

        return ReportResponse(
            report_type=report_type,
            generated_at=now,
            platform_overview=platform_overview,
            threat_intelligence=threat_intelligence,
            investigations=investigations,
            feed_statistics=feed_stats
        )

    @staticmethod
    def generate_csv(report: ReportResponse) -> str:
        """Converts the report into a multi-section CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([f"Threat Intelligence Report: {report.report_type.upper()}"])
        writer.writerow([f"Generated At: {report.generated_at.isoformat()}"])
        writer.writerow([])
        
        # Platform Overview
        writer.writerow(["--- PLATFORM OVERVIEW ---"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Indicators", report.platform_overview.total_indicators])
        writer.writerow(["New Indicators (24h)", report.platform_overview.new_indicators])
        writer.writerow(["Active Feeds", report.platform_overview.active_feeds])
        writer.writerow(["Feed Health %", report.platform_overview.feed_health_percentage])
        writer.writerow(["Open Investigations", report.platform_overview.open_investigations])
        writer.writerow(["Active Watchlist Matches", report.platform_overview.active_watchlist_matches])
        writer.writerow([])
        
        # Threat Intelligence
        writer.writerow(["--- THREAT INTELLIGENCE ---"])
        def write_top(title, items):
            writer.writerow([title])
            if not items:
                writer.writerow(["None", "0"])
            for item in items:
                writer.writerow([item.name, item.count])
            writer.writerow([])
            
        write_top("Top Malware", report.threat_intelligence.top_malware)
        write_top("Top Threat Actors", report.threat_intelligence.top_threat_actors)
        write_top("Top Campaigns", report.threat_intelligence.top_campaigns)
        write_top("Top MITRE Techniques", report.threat_intelligence.top_mitre_techniques)
        write_top("Top Vulnerabilities", report.threat_intelligence.top_vulnerabilities)
        write_top("Most Active Countries", report.threat_intelligence.most_active_countries)
        
        # Investigations
        writer.writerow(["--- INVESTIGATIONS ---"])
        writer.writerow(["Total", report.investigations.statistics.total])
        writer.writerow(["Open", report.investigations.statistics.open])
        writer.writerow(["Closed", report.investigations.statistics.closed])
        writer.writerow([])
        
        # Feed Statistics
        writer.writerow(["--- FEED STATISTICS ---"])
        writer.writerow(["Feed Name", "Status", "Total Imports", "Failed Runs", "Avg Runtime (s)"])
        for f in report.feed_statistics.feeds:
            writer.writerow([f.name, f.status, f.total_imports, f.failed_runs, f"{f.average_runtime_seconds:.2f}"])
            
        return output.getvalue()

    @staticmethod
    def generate_pdf(report: ReportResponse) -> bytes:
        """Converts the report into a PDF document."""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"Threat Intelligence Report: {report.report_type.upper()}", ln=True, align="C")
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 10, f"Generated At: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", ln=True, align="C")
        pdf.ln(10)
        
        # Helper function
        def add_section_header(title):
            pdf.set_font("helvetica", "B", 12)
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(0, 8, title, ln=True, fill=True)
            pdf.ln(2)
            
        def add_kv(k, v):
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(60, 6, str(k))
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, str(v), ln=True)

        def add_list(title, items):
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, title, ln=True)
            pdf.set_font("helvetica", "", 10)
            if not items:
                pdf.cell(10)
                pdf.cell(0, 6, "No data available", ln=True)
            else:
                for item in items:
                    pdf.cell(10)
                    pdf.cell(100, 6, str(item.name))
                    pdf.cell(0, 6, str(item.count), ln=True)
            pdf.ln(2)

        # Platform Overview
        add_section_header("Platform Overview")
        add_kv("Total Indicators:", report.platform_overview.total_indicators)
        add_kv("New Indicators (24h):", report.platform_overview.new_indicators)
        add_kv("Active Feeds:", report.platform_overview.active_feeds)
        add_kv("Feed Health:", f"{report.platform_overview.feed_health_percentage}%")
        add_kv("Open Investigations:", report.platform_overview.open_investigations)
        add_kv("Watchlist Matches:", report.platform_overview.active_watchlist_matches)
        pdf.ln(5)
        
        # Threat Intelligence
        add_section_header("Threat Intelligence")
        add_list("Top Malware", report.threat_intelligence.top_malware)
        add_list("Top Threat Actors", report.threat_intelligence.top_threat_actors)
        add_list("Top Campaigns", report.threat_intelligence.top_campaigns)
        add_list("Top Vulnerabilities", report.threat_intelligence.top_vulnerabilities)
        add_list("Top MITRE Techniques", report.threat_intelligence.top_mitre_techniques)
        add_list("Most Active Countries", report.threat_intelligence.most_active_countries)
        
        # Investigations
        add_section_header("Investigations Statistics")
        add_kv("Total Investigations:", report.investigations.statistics.total)
        add_kv("Open Investigations:", report.investigations.statistics.open)
        add_kv("Closed Investigations:", report.investigations.statistics.closed)
        pdf.ln(5)
        
        # Feed Statistics
        add_section_header("Feed Statistics")
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(60, 6, "Feed Name", border=1)
        pdf.cell(30, 6, "Status", border=1)
        pdf.cell(30, 6, "Imports", border=1)
        pdf.cell(30, 6, "Failed Runs", border=1)
        pdf.cell(40, 6, "Avg Runtime (s)", border=1, ln=True)
        
        pdf.set_font("helvetica", "", 9)
        for f in report.feed_statistics.feeds:
            pdf.cell(60, 6, str(f.name)[:30], border=1)
            pdf.cell(30, 6, str(f.status), border=1)
            pdf.cell(30, 6, str(f.total_imports), border=1)
            pdf.cell(30, 6, str(f.failed_runs), border=1)
            pdf.cell(40, 6, f"{f.average_runtime_seconds:.2f}", border=1, ln=True)
            
        return bytes(pdf.output())
