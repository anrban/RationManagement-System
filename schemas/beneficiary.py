from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BeneficiaryCreate(BaseModel):
    national_id: str
    ration_card_no: Optional[str] = None
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    household_size: int = 1
    income_bracket: Optional[str] = None


class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    household_size: Optional[int] = None
    income_bracket: Optional[str] = None
    is_active: Optional[bool] = None


class BeneficiaryVerify(BaseModel):
    verification_status: str  # verified / rejected / duplicate
    remarks: Optional[str] = None


class BeneficiaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    national_id: str
    ration_card_no: Optional[str] = None
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    household_size: int
    income_bracket: Optional[str] = None
    verification_status: str
    is_active: bool
    created_at: datetime
