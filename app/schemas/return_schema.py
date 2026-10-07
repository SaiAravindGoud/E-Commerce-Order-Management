from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReturnCreate(BaseModel):
    reason: str = Field(min_length=1)


class ReturnReject(BaseModel):
    rejection_reason: str = Field(min_length=1)


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    reason: str
    status: str
    refund_amount: Decimal
    rejection_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)