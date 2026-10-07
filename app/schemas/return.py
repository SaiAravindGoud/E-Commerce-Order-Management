from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ReturnStatus(str, Enum):
    REQUESTED = "Requested"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REFUNDED = "Refunded"


class ReturnCreate(BaseModel):
    reason: str = Field(
        min_length=5,
        max_length=1000,
    )


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    reason: str
    status: ReturnStatus
    refund_amount: Decimal | None
    rejection_reason: str | None

    model_config = ConfigDict(from_attributes=True)


class ReturnReject(BaseModel):
    rejection_reason: str = Field(
        min_length=5,
        max_length=1000,
    )