from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.order_return import OrderReturn
from app.models.user import User
from app.schemas.return_schema import (
    ReturnCreate,
    ReturnReject,
    ReturnResponse,
)


router = APIRouter(
    prefix="/orders",
    tags=["Returns"],
)


@router.post(
    "/{order_id}/returns",
    response_model=ReturnResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_return(
    order_id: int,
    return_data: ReturnCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.customer_id == current_user.id,
        )
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.status != "Delivered":
        raise HTTPException(
            status_code=400,
            detail="Returns are allowed only for delivered orders",
        )

    if order.delivered_at is None:
        raise HTTPException(
            status_code=400,
            detail="Delivery date is not available",
        )

    if datetime.now() > order.delivered_at + timedelta(days=7):
        raise HTTPException(
            status_code=400,
            detail="Return window of 7 days has expired",
        )

    existing_return = db.scalar(
        select(OrderReturn).where(
            OrderReturn.order_id == order_id
        )
    )

    if existing_return is not None:
        raise HTTPException(
            status_code=409,
            detail="Return already exists for this order",
        )

    new_return = OrderReturn(
        order_id=order.id,
        reason=return_data.reason,
        status="Requested",
        refund_amount=Decimal("0.00"),
    )

    db.add(new_return)
    db.commit()
    db.refresh(new_return)

    return new_return


@router.get(
    "/returns",
    response_model=list[ReturnResponse],
)
def get_my_returns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(OrderReturn)
        .join(Order, OrderReturn.order_id == Order.id)
        .order_by(OrderReturn.id.desc())
    )

    if current_user.role != "Admin":
        query = query.where(
            Order.customer_id == current_user.id
        )

    returns = db.scalars(query).all()

    return returns


@router.put(
    "/returns/{return_id}/approve",
    response_model=ReturnResponse,
)
def approve_return(
    return_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return_request = db.scalar(
        select(OrderReturn).where(
            OrderReturn.id == return_id
        )
    )

    if return_request is None:
        raise HTTPException(
            status_code=404,
            detail="Return not found",
        )

    if return_request.status != "Requested":
        raise HTTPException(
            status_code=400,
            detail="Only requested returns can be approved",
        )

    order = db.get(Order, return_request.order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    for item in order.items:
        product = db.get(Product, item.product_id)

        if product is not None:
            product.stock_quantity += item.quantity

    return_request.refund_amount = Decimal(
        str(order.grand_total)
    )

    return_request.status = "Refunded"

    order.payment_status = "Refunded"

    db.commit()
    db.refresh(return_request)

    return return_request


@router.put(
    "/returns/{return_id}/reject",
    response_model=ReturnResponse,
)
def reject_return(
    return_id: int,
    reject_data: ReturnReject,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return_request = db.scalar(
        select(OrderReturn).where(
            OrderReturn.id == return_id
        )
    )

    if return_request is None:
        raise HTTPException(
            status_code=404,
            detail="Return not found",
        )

    if return_request.status != "Requested":
        raise HTTPException(
            status_code=400,
            detail="Only requested returns can be rejected",
        )

    if not reject_data.rejection_reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required",
        )

    return_request.status = "Rejected"

    return_request.rejection_reason = (
        reject_data.rejection_reason
    )

    db.commit()
    db.refresh(return_request)

    return return_request