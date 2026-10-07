from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, get_current_user
from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def product_response(product: Product, db: Session) -> ProductResponse:
    rating_data = (
        db.query(
            func.avg(Review.rating).label("average_rating"),
            func.count(Review.id).label("review_count"),
        )
        .filter(Review.product_id == product.id)
        .first()
    )

    average_rating = float(rating_data.average_rating or 0)
    review_count = int(rating_data.review_count or 0)

    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        description=product.description,
        category_id=product.category_id,
        price=product.price,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
        average_rating=average_rating,
        review_count=review_count,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    category = (
        db.query(Category)
        .filter(Category.id == product_data.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    existing_sku = (
        db.query(Product)
        .filter(Product.sku == product_data.sku)
        .first()
    )

    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
        )

    product = Product(
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
        category_id=product_data.category_id,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        is_active=product_data.is_active,
    )

    db.add(product)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product could not be created",
        )

    return product_response(product, db)


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str | None = None,
    category_id: int | None = Query(None, gt=0),
    min_price: Decimal | None = Query(None, gt=0),
    max_price: Decimal | None = Query(None, gt=0),
    in_stock: bool | None = None,
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)

    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if in_stock is True:
        query = query.filter(Product.stock_quantity > 0)

    if in_stock is False:
        query = query.filter(Product.stock_quantity == 0)

    if sort_by not in {"price", "created_at"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be price or created_at",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order must be asc or desc",
        )

    sort_column = (
        Product.price
        if sort_by == "price"
        else Product.created_at
    )

    query = query.order_by(
        asc(sort_column) if order == "asc" else desc(sort_column)
    )

    products = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        product_response(product, db)
        for product in products
    ]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.is_active == True,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product_response(product, db)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    category = (
        db.query(Category)
        .filter(Category.id == product_data.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    duplicate_sku = (
        db.query(Product)
        .filter(
            Product.sku == product_data.sku,
            Product.id != product_id,
        )
        .first()
    )

    if duplicate_sku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
        )

    product.name = product_data.name
    product.sku = product_data.sku
    product.description = product_data.description
    product.category_id = product_data.category_id
    product.price = product_data.price
    product.stock_quantity = product_data.stock_quantity
    product.is_active = product_data.is_active

    db.commit()
    db.refresh(product)

    return product_response(product, db)


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.is_active = False

    db.commit()
    db.refresh(product)

    return product_response(product, db)