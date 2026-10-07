from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    product_id: int = Field(
        gt=0,
    )

    quantity: int = Field(
        ge=1,
    )


class CartItemUpdate(BaseModel):
    quantity: int = Field(
        ge=1,
    )


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    id: int
    customer_id: int
    items: list[CartItemResponse]
    subtotal: Decimal