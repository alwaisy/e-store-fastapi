from fastapi import FastAPI as App

from app.product.endpoint import product_router

version = 'v1'
version_prefix =f"/api/{version}"

app = App(
    title="FastApi Store",
    description="A learning / practice but professional level project.",
    version= version,
    # lifespan=life_span
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

app.include_router(product_router, prefix=f"/api/{version}/products", tags=['products'])