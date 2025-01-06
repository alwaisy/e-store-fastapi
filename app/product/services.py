# index
# show
# store
# update
# destroy

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Product
from .schema import ProductMutationSchema


class ProductService:
    async def index(self, session: AsyncSession):
        query = select(Product).order_by(desc(Product.created_at))
        response = await session.exec(query)

        return response.all()

    async def show(self, session: AsyncSession, productId: str):
        query = select(Product).where(Product.id == productId)
        response = await session.exec(query)
        product = response.one()

        return product if product else None

    async def store(self, session: AsyncSession, product_data: ProductMutationSchema):
        product_dict = product_data.model_dump()
        new_product = Product(**product_dict)
        # print(Product(**product_dict))
        session.add(new_product)
        await session.commit()

        return new_product

    async def update(self, session: AsyncSession, product_id: str, product: ProductMutationSchema):
        product_update = await self.show(session, product_id)

        if product_update is not None:
            product_update_dict = product.model_dump()
            for k, v in product_update_dict.items():
                setattr(product_update, k, v)

            await session.commit()

            return product_update
        else:
            return None

    async def destroy(self, session: AsyncSession, product_id: str):
        product_delete = await self.show(session, product_id)
        if product_delete is not None:
            await session.delete(product_delete)
            await session.commit()
        else:
            return None
