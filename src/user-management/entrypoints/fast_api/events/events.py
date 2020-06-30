from typing import Callable

from fastapi import FastAPI
from loguru import logger
from fastapi_contrib.tracing.middlewares import OpentracingMiddleware
from fastapi_contrib.tracing.utils import setup_opentracing


def setup_jaeger(app: FastAPI):
    setup_opentracing(app)
    app.add_middleware(OpentracingMiddleware)


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")
