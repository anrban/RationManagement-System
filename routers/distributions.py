import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from database import get_db
from models import Beneficiary, DistributionLog, AuditLog
from schemas.distribution import DistributionCreate, DistributionResponse
from auth.jwt import get_current_user
from auth.rbac import require_permission

router = APIRouter()


@router.post("/record", response_model=DistributionResponse, status_code=status.HTTP_201_CREATED)
def record_distribution(
    data: DistributionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("write_distribution")),
):
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == data.beneficiary_id
    ).first()
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    log = DistributionLog(
        beneficiary_id=data.beneficiary_id,
        ration_type=data.ration_type,
        quantity_kg=data.quantity_kg,
        unit_price=data.unit_price,
        total_value=data.total_value,
        distributed_by=current_user.id,
        distribution_center=data.distribution_center,
        qr_code_hash=data.qr_code_hash,
        remarks=data.remarks,
    )
    db.add(log)
    db.commit()

    audit = AuditLog(
        beneficiary_id=data.beneficiary_id,
        action="DISTRIBUTION",
        performed_by=current_user.id,
        metadata_json=json.dumps({
            "ration_type": data.ration_type,
            "quantity_kg": data.quantity_kg,
        }),
        ip_address=request.client.host if request.client else None,
    )
    db.add(audit)
    db.commit()
    db.refresh(log)
    return _to_response(log)


@router.get("/logs")
def list_distribution_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("read")),
):
    query = db.query(DistributionLog)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_to_response(d) for d in items],
    }


@router.get("/{distribution_id}", response_model=DistributionResponse)
def get_distribution(
    distribution_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("read")),
):
    log = db.query(DistributionLog).filter(DistributionLog.id == distribution_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Distribution log not found")
    return _to_response(log)


def _to_response(d: DistributionLog) -> DistributionResponse:
    return DistributionResponse(
        id=str(d.id),
        beneficiary_id=str(d.beneficiary_id),
        ration_type=d.ration_type.value if hasattr(d.ration_type, "value") else d.ration_type,
        quantity_kg=d.quantity_kg,
        unit_price=d.unit_price,
        total_value=d.total_value,
        distributed_by=str(d.distributed_by),
        distribution_center=d.distribution_center,
        delivered_at=d.delivered_at,
        acknowledged=d.acknowledged,
        qr_code_hash=d.qr_code_hash,
        remarks=d.remarks,
    )
