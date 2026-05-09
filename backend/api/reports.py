from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..schemas.report import ReportGenerateRequest, ReportSummaryResponse
from ..services import mock_data

router = APIRouter()


@router.get("/api/reports", response_model=list[ReportSummaryResponse])
def list_reports():
    if mock_data.is_enabled():
        return mock_data.get_reports() or []
    return []


@router.post("/api/reports")
def create_report(body: ReportGenerateRequest):
    raise HTTPException(status_code=501, detail="Report generation coming in Phase 2")


@router.get("/api/reports/{report_id}")
def get_report(report_id: str):
    raise HTTPException(status_code=501, detail="Report generation coming in Phase 2")
