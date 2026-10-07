
from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.category import router as category_router
from app.routers.product import router as product_router
from app.routers.cart import router as cart_router
from app.routers.address import router as address_router
from app.routers.order import router as order_router
from app.routers.payment import router as payment_router
from app.routers.returns import router as return_router
from app.routers.review import router as review_router
from app.routers.reports import router as reports_router


app = FastAPI(
    title="E-Commerce Order Management API",
    description="Backend API for E-Commerce Order Management System",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(address_router)

# Returns router must come before the dynamic /orders/{order_id} route
app.include_router(return_router)
app.include_router(order_router)
app.include_router(payment_router)

# Reviews
app.include_router(review_router)

# Reports
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "E-Commerce Order Management API is running"
    }
