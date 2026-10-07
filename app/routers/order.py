
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.address import Address
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderResponse
from app.auth.dependencies import get_current_user
from app.services.email_service import send_email


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = db.scalar(
        select(Cart).where(Cart.customer_id == current_user.id)
    )

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    cart_items = db.scalars(
        select(CartItem).where(CartItem.cart_id == cart.id)
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    address = db.scalar(
        select(Address).where(
            Address.customer_id == current_user.id,
            Address.is_default.is_(True),
        )
    )

    if address is None:
        address = db.scalar(
            select(Address).where(
                Address.customer_id == current_user.id
            )
        )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add an address before placing an order",
        )

    subtotal = Decimal("0.00")
    order_items_data = []

    for cart_item in cart_items:
        product = db.get(Product, cart_item.product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {cart_item.product_id} not found",
            )

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is inactive",
            )

        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available stock: {product.stock_quantity}"
                ),
            )

        item_subtotal = product.price * cart_item.quantity
        subtotal += item_subtotal

        order_items_data.append(
            {
                "product": product,
                "quantity": cart_item.quantity,
                "unit_price": product.price,
            }
        )

    # 18% GST
    tax = subtotal * Decimal("0.18")

    # ₹50 delivery for orders of ₹500 or less
    # Free delivery for orders above ₹500
    delivery_charge = (
        Decimal("0.00")
        if subtotal > Decimal("500.00")
        else Decimal("50.00")
    )

    grand_total = subtotal + tax + delivery_charge

    existing_orders = db.scalars(
        select(Order).where(
            Order.customer_id == current_user.id
        )
    ).all()

    order_number = (
        f"ORD-{current_user.id}-{len(existing_orders) + 1:04d}"
    )

    order = Order(
        order_number=order_number,
        customer_id=current_user.id,
        address_id=address.id,
        subtotal=subtotal,
        tax_amount=tax,
        delivery_charge=delivery_charge,
        grand_total=grand_total,
        status="Pending",
        payment_status="Unpaid",
    )

    db.add(order)
    db.flush()

    for item_data in order_items_data:
        product = item_data["product"]
        quantity = item_data["quantity"]
        unit_price = item_data["unit_price"]

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=unit_price * quantity,
        )

        db.add(order_item)

        product.stock_quantity -= quantity

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    background_tasks.add_task(
        send_email,
        current_user.email,
        "Order Confirmation - E-Commerce",
        (
            f"Hello {current_user.username},\n\n"
            f"Your order has been placed successfully.\n\n"
            f"Order Number: {order.order_number}\n"
            f"Order Total: ₹{order.grand_total}\n"
            f"Order Status: {order.status}\n"
            f"Payment Status: {order.payment_status}\n\n"
            "Thank you for shopping with us."
        ),
    )

    return order


@router.get(
    "",
    response_model=list[OrderResponse],
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = db.scalars(
        select(Order)
        .where(Order.customer_id == current_user.id)
        .order_by(Order.id.desc())
    ).all()

    return orders


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    return order


@router.put(
    "/{order_id}/cancel",
)
def cancel_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
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

        if order.status not in ["Pending", "Confirmed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only Pending or Confirmed orders "
                    "can be cancelled"
                ),
            )

        for item in order.items:
            product = db.get(Product, item.product_id)

            if product is not None:
                product.stock_quantity += item.quantity

        order.status = "Cancelled"

        if order.payment_status == "Paid":
            order.payment_status = "Refunded"

        db.commit()
        db.refresh(order)

        background_tasks.add_task(
            send_email,
            current_user.email,
            "Order Cancelled - E-Commerce",
            (
                f"Hello {current_user.username},\n\n"
                f"Your order has been cancelled successfully.\n\n"
                f"Order Number: {order.order_number}\n"
                f"Order Status: {order.status}\n"
                f"Payment Status: {order.payment_status}\n\n"
                "Thank you."
            ),
        )

        return {
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "status": order.status,
            "payment_status": order.payment_status,
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.put(
    "/{order_id}/status",
)
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Shipped",
        "Delivered",
        "Cancelled",
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status. Allowed values: "
                f"{', '.join(allowed_statuses)}"
            ),
        )

    status_order = {
        "Pending": 1,
        "Confirmed": 2,
        "Shipped": 3,
        "Delivered": 4,
        "Cancelled": 5,
    }

    if (
        order.status != "Cancelled"
        and new_status != "Cancelled"
        and status_order[new_status] < status_order[order.status]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order status cannot move backward",
        )

    order.status = new_status

    if new_status == "Delivered":
        from datetime import datetime

        order.delivered_at = datetime.now()

        # COD/unpaid orders become paid when delivered
        if order.payment_status == "Unpaid":
            order.payment_status = "Paid"

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
    }
