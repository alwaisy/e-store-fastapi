from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.auth.dependencies import AccessTokenBearer, RoleChecker
from app.db.main import get_session
from app.errors import ProductNotFound
from .models import Product
from .schema import ProductMutationSchema
from .services import ProductService

product_router = APIRouter()
product_service = ProductService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin"])


@product_router.get("/", response_model=List[Product])
async def read(session: AsyncSession = Depends(get_session)) -> List[Product]:
    products = await product_service.index(session)

    return products


@product_router.get("/{id}", response_model=Product)
async def read_one(
    session: AsyncSession = Depends(get_session), id: str = None
) -> Product:
    product = await product_service.show(session, id)

    return product if product else ProductNotFound()


@product_router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductMutationSchema,
    dependencies=[Depends(access_token_bearer), Depends(role_checker)],
)
async def create(
    product: Product,
    session: AsyncSession = Depends(get_session),
):
    return await product_service.store(session, product)


@product_router.patch(
    "/{id}/update",
    response_model=ProductMutationSchema,
    dependencies=[Depends(access_token_bearer), Depends(role_checker)],
)
async def update(
    id: str,
    product: Product,
    session: AsyncSession = Depends(get_session),
) -> dict:
    try:
        updated_product = await product_service.update(session, id, product)
        return updated_product
    except:
        raise HTTPException(status_code=404, detail="Product not found")


@product_router.delete(
    "/{id}/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(access_token_bearer), Depends(role_checker)],
)
async def delete(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        await product_service.destroy(session, id)
        return JSONResponse(
            content={"method": "delete", "message": f"Product with id {id} deleted"},
            status_code=200,
        )

    except:
        raise HTTPException(status_code=404, detail="Product not found")
