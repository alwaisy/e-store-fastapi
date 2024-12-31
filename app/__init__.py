from contextlib import asynccontextmanager

from fastapi import FastAPI as App, FastAPI

from app.db.main import init_db
from app.errors import register_all_errors
from app.product.routes import product_router

version = 'v1'
version_prefix =f"/api/{version}"

#the lifespan event / need in dev server especially to create tables in db
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Server is starting...")
#     await init_db()
#     yield
#     print("server is stopping")

app = App(
    title="FastApi Store",
    description="A learning / practice but professional level project.",
    version= version,
    # lifespan=lifespan,
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_all_errors(app)

app.include_router(product_router, prefix=f"/api/{version}/products", tags=['products'])