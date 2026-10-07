from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TimestampResponse(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int


class DecimalResponse(BaseModel):
    amount: Decimal