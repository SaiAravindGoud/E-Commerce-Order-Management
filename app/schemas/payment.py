from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "Card"
    NET_BANKING = "Net Banking"
    COD = "COD"


class PaymentStatus(str, Enum):
    SUCCESS = "Success"
    FAILED = "Failed"


class PaymentCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
    )

    payment_method: PaymentMethod

    transaction_id: str = Field(
        min_length=3,
        max_length=100,
    )

    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: PaymentMethod
    transaction_id: str
    status: PaymentStatus

    model_config = ConfigDict(from_attributes=True)