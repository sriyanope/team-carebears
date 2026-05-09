from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import dashboard as dashboard_service
from ..schemas.dashboard import DashboardResponse

router = APIRouter()


@router.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard(db)
