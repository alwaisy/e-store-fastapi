from fastapi import FastAPI as App

from .auth.routes import auth_router
from .db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware
from .product.routes import product_router

version = "v1"
version_prefix = f"/api/{version}"

# the lifespan event / need in dev server especially to create tables in db
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Server is starting...")
#     await init_db()
#     yield
#     print("server is stopping")

app = App(
    title="FastApi Store",
    description="A learning / practice but professional level project.",
    version=version,
    # lifespan=lifespan,
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
)

register_all_errors(app)
register_middleware(app)

app.include_router(product_router, prefix=f"/api/{version}/products", tags=["products"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
