
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_admin
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.order_return import OrderReturn


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/sales")
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(
        end_date + timedelta(days=1),
        time.min,
    )

    total_orders = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime,
        )
    ) or 0

    total_revenue = db.scalar(
        select(func.coalesce(func.sum(Order.grand_total), 0)).where(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime,
            Order.payment_status == "Paid",
            Order.status != "Cancelled",
        )
    ) or Decimal("0.00")

    total_refunds = db.scalar(
        select(func.coalesce(func.sum(OrderReturn.refund_amount), 0)).where(
            OrderReturn.created_at >= start_datetime,
            OrderReturn.created_at < end_datetime,
            OrderReturn.status == "Refunded",
        )
    ) or Decimal("0.00")

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_refunds": total_refunds,
    }


@router.get("/orders-by-status")
def orders_by_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    rows = db.execute(
        select(
            Order.status,
            func.count(Order.id).label("count"),
        )
        .group_by(Order.status)
        .order_by(Order.status)
    ).all()

    return [
        {
            "status": row.status,
            "count": row.count,
        }
        for row in rows
    ]


@router.get("/top-products")
def top_products(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    rows = db.execute(
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.sum(OrderItem.quantity).label("total_quantity"),
        )
        .join(
            OrderItem,
            OrderItem.product_id == Product.id,
        )
        .join(
            Order,
            Order.id == OrderItem.order_id,
        )
        .where(Order.status != "Cancelled")
        .group_by(
            Product.id,
            Product.name,
        )
        .order_by(
            func.sum(OrderItem.quantity).desc()
        )
        .limit(5)
    ).all()

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "total_quantity": row.total_quantity,
        }
        for row in rows
    ]


@router.get("/low-stock")
def low_stock_products(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    rows = db.execute(
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.sku,
            Product.stock_quantity,
        )
        .where(
            Product.stock_quantity < 5,
            Product.is_active == True,
        )
        .order_by(Product.stock_quantity.asc())
    ).all()

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "sku": row.sku,
            "stock_quantity": row.stock_quantity,
        }
        for row in rows
    ]
