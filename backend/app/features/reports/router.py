"""Reports API router."""

import time
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.reports.schemas import ReportResponse
from app.features.reports.service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])

VALID_TYPES = {"daily", "weekly", "monthly", "executive"}


def _generate(db: Session, report_type: str) -> ReportResponse:
    if report_type not in VALID_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown report type: {report_type}")
    
    t0 = time.monotonic()
    try:
        report = ReportService.generate_report(db, report_type)
        duration = time.monotonic() - t0
        logger.info(f"Report generated. type={report_type}, duration={duration:.3f}s")
        return report
    except Exception as e:
        duration = time.monotonic() - t0
        logger.error(f"Report generation failed. type={report_type}, duration={duration:.3f}s, error={e}")
        raise


@router.get("/daily", response_model=ReportResponse)
def get_daily_report(db: Session = Depends(get_db)):
    """Get the daily intelligence report."""
    return _generate(db, "daily")


@router.get("/weekly", response_model=ReportResponse)
def get_weekly_report(db: Session = Depends(get_db)):
    """Get the weekly intelligence report."""
    return _generate(db, "weekly")


@router.get("/monthly", response_model=ReportResponse)
def get_monthly_report(db: Session = Depends(get_db)):
    """Get the monthly intelligence report."""
    return _generate(db, "monthly")


@router.get("/executive", response_model=ReportResponse)
def get_executive_report(db: Session = Depends(get_db)):
    """Get the executive summary report."""
    return _generate(db, "executive")


@router.get("/{report_type}/export")
def export_report(
    report_type: str,
    format: str = Query(..., description="Export format: json, csv, or pdf"),
    db: Session = Depends(get_db)
):
    """Export a report in the specified format."""
    format = format.lower()
    if format not in {"json", "csv", "pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported export format. Use json, csv, or pdf.")
        
    report = _generate(db, report_type)
    
    if format == "json":
        return report

    if format == "csv":
        try:
            csv_content = ReportService.generate_csv(report)
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="report_{report_type}.csv"'}
            )
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate CSV")

    if format == "pdf":
        try:
            pdf_content = ReportService.generate_pdf(report)
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="report_{report_type}.pdf"'}
            )
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
