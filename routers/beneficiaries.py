import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Beneficiary, AuditLog, VerificationStatus
from schemas.beneficiary import BeneficiaryCreate, BeneficiaryResponse, BeneficiaryVerify
from auth.jwt import get_current_user
from auth.rbac import require_permission
from services.deduplication import check_for_duplicates

router = APIRouter()


@router.post("/register", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def register_beneficiary(
    data: BeneficiaryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("write")),
):
    existing = db.query(Beneficiary).filter(
        Beneficiary.national_id == data.national_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Beneficiary with this national ID already exists"
        )

    duplicates = check_for_duplicates(data.model_dump(), db)
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Potential duplicates found", "duplicates": duplicates}
        )

    beneficiary = Beneficiary(
        national_id=data.national_id,
        ration_card_no=data.ration_card_no,
        name=data.name,
        phone=data.phone,
        address=data.address,
        district=data.district,
        household_size=data.household_size,
        income_bracket=data.income_bracket,
    )
    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    return _to_response(beneficiary)


@router.post("/{beneficiary_id}/verify", response_model=BeneficiaryResponse)
def verify_beneficiary(
    beneficiary_id: str,
    data: BeneficiaryVerify,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("write")),
):
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == beneficiary_id
    ).first()
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    from datetime import datetime
    beneficiary.verification_status = data.verification_status
    beneficiary.verified_by = current_user.id
    beneficiary.verified_at = datetime.utcnow()
    db.commit()

    audit = AuditLog(
        beneficiary_id=beneficiary.id,
        action="VERIFIED",
        performed_by=current_user.id,
        metadata_json=json.dumps({"status": data.verification_status, "remarks": data.remarks}),
        ip_address=request.client.host if request.client else None,
    )
    db.add(audit)
    db.commit()
    db.refresh(beneficiary)
    return _to_response(beneficiary)


@router.get("/{beneficiary_id}/history")
def get_beneficiary_history(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("read")),
):
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == beneficiary_id
    ).first()
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    from schemas.distribution import DistributionResponse
    history = []
    for d in beneficiary.distributions:
        history.append({
            "id": str(d.id),
            "ration_type": d.ration_type.value if hasattr(d.ration_type, "value") else d.ration_type,
            "quantity_kg": d.quantity_kg,
            "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
            "distribution_center": d.distribution_center,
            "acknowledged": d.acknowledged,
        })
    return {"beneficiary_id": beneficiary_id, "history": history}


@router.get("/")
def list_beneficiaries(
    district: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("read")),
):
    query = db.query(Beneficiary)
    if district:
        query = query.filter(Beneficiary.district == district)
    if status:
        query = query.filter(Beneficiary.verification_status == status)

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_to_response(b) for b in items],
    }


def _to_response(b: Beneficiary) -> BeneficiaryResponse:
    return BeneficiaryResponse(
        id=str(b.id),
        national_id=b.national_id,
        ration_card_no=b.ration_card_no,
        name=b.name,
        phone=b.phone,
        address=b.address,
        district=b.district,
        household_size=b.household_size,
        income_bracket=b.income_bracket,
        verification_status=b.verification_status.value if hasattr(b.verification_status, "value") else b.verification_status,
        is_active=b.is_active,
        created_at=b.created_at,
    )
