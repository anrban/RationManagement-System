from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Beneficiary, AuditLog, FraudFlag, User, VerificationStatus
from schemas.analytics import FraudFlagResponse
from auth.rbac import require_permission

router = APIRouter()


@router.post("/flag-duplicate", status_code=status.HTTP_201_CREATED)
def flag_duplicate(
    beneficiary_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("delete")),
):
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    beneficiary.verification_status = VerificationStatus.DUPLICATE
    db.commit()

    flag = FraudFlag(
        beneficiary_id=beneficiary_id,
        reason=reason,
        flagged_by=current_user.id,
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)

    return {
        "message": "Beneficiary flagged as duplicate",
        "flag_id": str(flag.id),
    }


@router.get("/audit-logs")
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("read")),
):
    query = db.query(AuditLog)
    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": str(a.id),
                "beneficiary_id": str(a.beneficiary_id) if a.beneficiary_id else None,
                "action": a.action,
                "performed_by": str(a.performed_by) if a.performed_by else None,
                "ip_address": a.ip_address,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            }
            for a in items
        ],
    }


@router.get("/users")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("manage_users")),
):
    query = db.query(User)
    total = query.count()
    users = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "role": u.role.value if hasattr(u.role, "value") else u.role,
                "district": u.district,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }
