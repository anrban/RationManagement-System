from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DistributionCreate(BaseModel):
    beneficiary_id: str
    ration_type: str
    quantity_kg: float
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    distribution_center: Optional[str] = None
    qr_code_hash: Optional[str] = None
    remarks: Optional[str] = None


class DistributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    beneficiary_id: str
    ration_type: str
    quantity_kg: float
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    distributed_by: str
    distribution_center: Optional[str] = None
    delivered_at: datetime
    acknowledged: bool
    qr_code_hash: Optional[str] = None
    remarks: Optional[str] = None
