from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.review import (
    ProductRatingResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/products/{product_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    product_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    existing_review = db.scalar(
        select(Review).where(
            Review.product_id == product_id,
            Review.customer_id == current_user.id,
        )
    )

    if existing_review is not None:
        raise HTTPException(
            status_code=409,
            detail="You have already reviewed this product",
        )

    purchased = db.scalar(
        select(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.customer_id == current_user.id,
            OrderItem.product_id == product_id,
            Order.status != "Cancelled",
        )
    )

    if purchased is None:
        raise HTTPException(
            status_code=403,
            detail="You can review only products you have purchased",
        )

    new_review = Review(
        product_id=product_id,
        customer_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.get(
    "/products/{product_id}",
    response_model=list[ReviewResponse],
)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    reviews = db.scalars(
        select(Review)
        .where(Review.product_id == product_id)
        .order_by(Review.id.desc())
    ).all()

    return reviews


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.get(Review, review_id)

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    if review.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can update only your own review",
        )

    review.rating = review_data.rating
    review.comment = review_data.comment

    db.commit()
    db.refresh(review)

    return review


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.get(Review, review_id)

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    if review.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own review",
        )

    db.delete(review)
    db.commit()

    return None


@router.get(
    "/products/{product_id}/rating",
    response_model=ProductRatingResponse,
)
def get_product_rating(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    average_rating, review_count = db.execute(
        select(
            func.coalesce(func.avg(Review.rating), 0),
            func.count(Review.id),
        ).where(
            Review.product_id == product_id
        )
    ).one()

    return {
        "average_rating": round(float(average_rating), 2),
        "review_count": review_count,
    }