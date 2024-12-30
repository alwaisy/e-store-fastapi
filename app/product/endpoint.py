# declare product routes
from fastapi import APIRouter

from app.product.service import ProductService

product_router = APIRouter()
product_service = ProductService()



product_router.get("/")(product_service.index)
