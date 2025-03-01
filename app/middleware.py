import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
from honeybadger import honeybadger, contrib

from app import Config

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

# honeybadger
honeybadger.configure(api_key=Config.ES_HONEYBADGER_API_KEY)


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            # "bookly-api-dc03.onrender.com",
            # "0.0.0.0",
            "62.169.28.254",
        ],
    )
    app.add_middleware(contrib.ASGIHoneybadger, params_filters=["dont-include-this"])
