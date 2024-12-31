from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.main import get_session
from app.db.models import Product
from app.errors import ProductNotFound
from app.product.schema import ProductMutationSchema
from app.product.services import ProductService

product_router = APIRouter()
product_service = ProductService()


@product_router.get("/", response_model=List[Product])
async def read(session: AsyncSession = Depends(get_session)) -> List[Product]:
    products = await product_service.index(session)

    return products


@product_router.get("/{id}", response_model=Product)
async def read_one(session: AsyncSession = Depends(get_session), id: str = None) -> Product:
    product = await product_service.show(session, id)

    return product if product else ProductNotFound()


@product_router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductMutationSchema
)
async def create(product: Product, session: AsyncSession = Depends(get_session)):
    return await product_service.store(session, product)


@product_router.patch("/{id}/update", response_model=ProductMutationSchema)
async def update(id: str, product: Product, session: AsyncSession = Depends(get_session)) -> dict:
    updated_product = await product_service.update(session, id, product)

    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    else:
        return updated_product
