from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
try:
    from geoalchemy2 import Geometry as _Geometry
    _HAS_GEOALCHEMY2 = True
except ImportError:
    _HAS_GEOALCHEMY2 = False
    _Geometry = None

import uuid
import enum
from datetime import datetime

from database import Base


# ─── Enums ───────────────────────────────────────────────

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    DISTRICT_OFFICER = "district_officer"
    FIELD_AGENT = "field_agent"
    AUDITOR = "auditor"


class RationType(str, enum.Enum):
    RICE = "rice"
    WHEAT = "wheat"
    OIL = "oil"
    SUGAR = "sugar"
    KEROSENE = "kerosene"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


# ─── User (Staff / Officers) ─────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    district = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Beneficiary ─────────────────────────────────────────

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_id = Column(String(20), unique=True, nullable=False)
    ration_card_no = Column(String(20), unique=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(15), unique=True)
    address = Column(Text)
    district = Column(String(100))
    household_size = Column(Integer, default=1)
    income_bracket = Column(String(50))  # BPL / APL / AAY
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    face_encoding = Column(Text)  # Base64 / vector for biometric deduplication
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    distributions = relationship("DistributionLog", back_populates="beneficiary")
    audit_logs = relationship("AuditLog", back_populates="beneficiary")


# ─── Distribution Log ────────────────────────────────────

class DistributionLog(Base):
    __tablename__ = "distribution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("beneficiaries.id"), nullable=False)
    ration_type = Column(Enum(RationType), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    unit_price = Column(Float)
    total_value = Column(Float)
    distributed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    distribution_center = Column(String(150))
    location = Column(_Geometry("POINT") if _HAS_GEOALCHEMY2 else Text)  # GPS coordinates
    delivered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)  # Beneficiary confirmation
    qr_code_hash = Column(String)  # QR scan proof
    signature_url = Column(String)  # S3/minio URL of signature image
    remarks = Column(Text)

    beneficiary = relationship("Beneficiary", back_populates="distributions")


# ─── Audit Log (Immutable trail) ─────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("beneficiaries.id"))
    action = Column(String(100))  # e.g., "VERIFIED", "DISTRIBUTION", "FLAGGED"
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    metadata_json = Column(Text)  # JSON blob with before/after state
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="audit_logs")


# ─── Fraud/Duplicate Flag ────────────────────────────────

class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("beneficiaries.id"))
    reason = Column(Text, nullable=False)
    flagged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
