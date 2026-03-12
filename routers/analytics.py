from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import DistributionLog, Beneficiary, FraudFlag
from schemas.analytics import SummaryResponse, TrendPoint, FraudFlagResponse
from auth.rbac import require_permission

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("view_analytics")),
):
    total_beneficiaries = db.query(func.count(Beneficiary.id)).scalar() or 0
    verified = db.query(func.count(Beneficiary.id)).filter(
        Beneficiary.verification_status == "verified"
    ).scalar() or 0
    total_distributions = db.query(func.count(DistributionLog.id)).scalar() or 0
    total_ration_kg = db.query(func.sum(DistributionLog.quantity_kg)).scalar()
    fraud_flags_open = db.query(func.count(FraudFlag.id)).filter(
        FraudFlag.resolved.is_(False)
    ).scalar() or 0
    coverage_rate = round((verified / total_beneficiaries) * 100, 2) if total_beneficiaries else 0.0

    return SummaryResponse(
        total_beneficiaries=total_beneficiaries,
        verified_beneficiaries=verified,
        total_distributions=total_distributions,
        total_ration_distributed_kg=total_ration_kg,
        open_fraud_flags=fraud_flags_open,
        coverage_rate=coverage_rate,
    )


@router.get("/distribution-trends")
def distribution_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("view_analytics")),
):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.query(
        func.date(DistributionLog.delivered_at).label("date"),
        func.count(DistributionLog.id).label("count"),
        func.sum(DistributionLog.quantity_kg).label("total_kg"),
    ).filter(
        DistributionLog.delivered_at >= since
    ).group_by(
        func.date(DistributionLog.delivered_at)
    ).all()

    return [
        TrendPoint(date=str(r.date), count=r.count, total_kg=r.total_kg)
        for r in results
    ]


@router.get("/fraud-flags")
def list_fraud_flags(
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("view_analytics")),
):
    flags = db.query(FraudFlag).filter(FraudFlag.resolved.is_(False)).all()
    return [
        FraudFlagResponse(
            id=str(f.id),
            beneficiary_id=str(f.beneficiary_id) if f.beneficiary_id else None,
            reason=f.reason,
            flagged_by=str(f.flagged_by) if f.flagged_by else None,
            resolved=f.resolved,
            created_at=f.created_at,
        )
        for f in flags
    ]
