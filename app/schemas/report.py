from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesReportResponse(BaseModel):
    start_date: date
    end_date: date
    total_orders: int
    total_revenue: Decimal
    total_refunds: Decimal


class OrderStatusCountResponse(BaseModel):
    status: str
    count: int


class TopProductResponse(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int

    model_config = ConfigDict(from_attributes=True)


class LowStockProductResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)