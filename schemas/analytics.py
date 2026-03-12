from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SummaryResponse(BaseModel):
    total_beneficiaries: int
    verified_beneficiaries: int
    total_distributions: int
    total_ration_distributed_kg: Optional[float]
    open_fraud_flags: int
    coverage_rate: float


class TrendPoint(BaseModel):
    date: str
    count: int
    total_kg: Optional[float]


class FraudFlagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    beneficiary_id: Optional[str] = None
    reason: str
    flagged_by: Optional[str] = None
    resolved: bool
    created_at: datetime
