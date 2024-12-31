from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import Config

async_engine = AsyncEngine(create_engine(url=Config.ES_DB, echo=False))


async def init_db() -> None:
    async with async_engine.begin() as conn:
        # import model that is responsible to create table in db
        # from app.db.models import Product
        # print('connecting db')
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    Session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session
