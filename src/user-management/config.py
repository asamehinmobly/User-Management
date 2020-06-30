import datetime
import logging
import sys
from typing import List

from loguru import logger
from pydantic import BaseSettings
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from entrypoints.fast_api.logging.logging import InterceptHandler
from fastapi_contrib.conf import settings

API_PREFIX = "/api"

JWT_TOKEN_PREFIX = "Token"  # noqa: S105
VERSION = "0.0.0"

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)
DB_HOST: str = config("DB_HOST")
DB_PASSWORD: str = config("DB_PASSWORD", default='root')
DB_USER: str = config("DB_USER", default='root')
DB_PORT: int = config("DB_PORT", cast=int, default=3306)
DB_NAME: str = config("DB_NAME")
API_HOST: str = config("API_HOST", default='localhost')
API_PORT: int = config("API_PORT", cast=int, default=80)
REDIS_HOST: str = config("REDIS_HOST", default='localhost')
REDIS_PORT: int = config("REDIS_PORT", cast=int, default=6379)
EMAIL_HOST: str = config("EMAIL_HOST", default='localhost')
EMAIL_PORT: int = config("EMAIL_PORT", cast=int, default=1025)
EMAIL_HTTP_PORT: int = config("EMAIL_HTTP_PORT", cast=int, default=8025)

JAEGER_HOST: str = config("JAEGER_HOST", default='localhost')
JAEGER_PORT: int = config("JAEGER_PORT", cast=int, default=5775)
JAEGER_SAMPLER_RATE: float = config("JAEGER_SAMPLER_RATE", cast=float, default=5775)
JAEGER_SAMPLER_TYPE: str = config("JAEGER_SAMPLER_TYPE", default='probabilistic')
JAEGER_TRACE_ID_HEADER: str = config("JAEGER_TRACE_ID_HEADER", default='X-TRACE-ID')

BROKER_HOST: str = config('BROKER_HOST')
BROKER_PORT: int = config('BROKER_PORT')
BROKER_USERNAME: str = config('BROKER_USERNAME')
BROKER_PASSWORD: str = config('BROKER_PASSWORD')
BROKER_VHOST: str = config('BROKER_VHOST')
BROKER_EXCHANGE: str = config('BROKER_EXCHANGE')
BROKER_TEMPLATE_QUEUE: str = config('BROKER_TEMPLATE_QUEUE')
BROKER_TEMPLATE_JOB_QUEUE: str = config('BROKER_TEMPLATE_JOB_QUEUE')

# OWNERS: dict = views.get_owners(uow=bus.uow)

IV: str = config('IV')
API_GATEWAY_KEY: str = config('API_GATEWAY_KEY')
RESET_PASS_TOKEN: int = int(config('RESET_PASS_TOKEN'))

JWT_SECRET_KEY: str = config('JWT_SECRET_KEY')
JWT_EXPIRES: datetime = datetime.timedelta(seconds=int(config('JWT_EXPIRATION_SECONDS')))

SUBSCRIPTION_BASE_URL: str = config('SUBSCRIPTION_BASE_URL')


def get_mysql_uri():
    return f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


def get_postgres_uri():
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_api_url():
    host = API_HOST
    port = 5005 if host == 'localhost' else 80
    return f"http://{host}:{port}"


def get_redis_host_and_port():
    host = REDIS_HOST
    port = REDIS_PORT
    return dict(host=host, port=port)


def get_email_host_and_port():
    host = EMAIL_HOST
    port = EMAIL_PORT
    http_port = EMAIL_HTTP_PORT
    return dict(host=host, port=port, http_port=http_port)


MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)

PROJECT_NAME: str = config("PROJECT_NAME", default="FastAPI inmobly user-management application")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="",
)

settings.jaeger_host = JAEGER_HOST
settings.jaeger_port = JAEGER_PORT
settings.jaeger_sampler_rate = JAEGER_SAMPLER_RATE
settings.jaeger_sampler_type = JAEGER_SAMPLER_TYPE
settings.trace_id_header = JAEGER_TRACE_ID_HEADER
settings.service_name = PROJECT_NAME
# logging configuration

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

# Old apps

OLD_APPS = {
    "2108af8fbe137d2181c9d0999b89cd3aa383d968b627c7f17fb6f2dd5a472233": "teletica",
    "c3d23178091bcda443e9191e0e416139527e4c92803be03ebc886662bd8ad837": "antv"
}
