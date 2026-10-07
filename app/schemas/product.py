from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    sku: str = Field(
        min_length=2,
        max_length=50,
    )

    description: str | None = None

    category_id: int = Field(
        gt=0,
    )

    price: Decimal = Field(
        gt=0,
    )

    stock_quantity: int = Field(
        ge=0,
    )

    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    sku: str = Field(
        min_length=2,
        max_length=50,
    )

    description: str | None = None

    category_id: int = Field(
        gt=0,
    )

    price: Decimal = Field(
        gt=0,
    )

    stock_quantity: int = Field(
        ge=0,
    )

    is_active: bool = True


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: str | None
    category_id: int
    price: Decimal
    stock_quantity: int
    is_active: bool
    average_rating: float
    review_count: int

    model_config = ConfigDict(from_attributes=True)