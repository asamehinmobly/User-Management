# pylint: disable=redefined-outer-name
import shutil
import subprocess
import time
from pathlib import Path

import pytest
import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay

from adapters.orm.orm import start_mappers
import config
from adapters.orm.singleton_meta_data import MetaDataSingleton

pytest.register_assert_rewrite('tests.e2e.api_client')


@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine('sqlite:///:memory:')
    MetaDataSingleton().get_instance().create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(in_memory_sqlite_db):
    yield sessionmaker(bind=in_memory_sqlite_db)


@pytest.fixture
def mappers():
    start_mappers()
    yield
    clear_mappers()


@retry(stop=stop_after_delay(10))
def wait_for_mysql_to_come_up(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_url())


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**config.get_redis_host_and_port())
    return r.ping()


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(config.get_mysql_uri(), isolation_level='SERIALIZABLE')
    wait_for_mysql_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def mysql_session_factory(mysql_db):
    yield sessionmaker(bind=mysql_db)


@pytest.fixture
def mysql_session(mysql_session_factory):
    return mysql_session_factory()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / '../src/user-management/entrypoints/fast_app.py').touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which('docker-compose'):
        print('skipping restart, assumes running in container')
        return
    subprocess.run(
        ['docker-compose', 'restart', '-t', '0', 'redis_pubsub'],
        check=True,
    )
