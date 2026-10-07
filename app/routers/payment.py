from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse


router = APIRouter(
    prefix="/orders",
    tags=["Payments"],
)


@router.post(
    "/{order_id}/pay",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    order_id: int,
    payment_data: PaymentCreate,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot make payment for a cancelled order",
        )

    if order.status == "Delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivered orders cannot be paid",
        )

    if order.payment_status == "Paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already paid",
        )

    if payment_data.amount != Decimal(str(order.grand_total)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must match order total",
        )

    existing_payment = db.scalar(
        select(Payment).where(
            Payment.transaction_id == payment_data.transaction_id
        )
    )

    if existing_payment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction ID already exists",
        )

    if payment_data.payment_method.value == "COD":
        payment = Payment(
            order_id=order.id,
            amount=payment_data.amount,
            payment_method="COD",
            transaction_id=payment_data.transaction_id,
            status="Success",
        )

        db.add(payment)
        order.status = "Confirmed"

        db.commit()
        db.refresh(payment)

        return payment

    payment = Payment(
        order_id=order.id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method.value,
        transaction_id=payment_data.transaction_id,
        status=payment_data.status.value,
    )

    db.add(payment)

    if payment_data.status.value == "Success":
        order.payment_status = "Paid"

        if order.status in ["Pending", "Confirmed"]:
            order.status = "Confirmed"

    db.commit()
    db.refresh(payment)

    return payment


@router.get(
    "/{order_id}/payments",
    response_model=list[PaymentResponse],
)
def get_order_payments(
    order_id: int,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    payments = db.scalars(
        select(Payment)
        .where(Payment.order_id == order_id)
        .order_by(Payment.id.desc())
    ).all()

    return payments