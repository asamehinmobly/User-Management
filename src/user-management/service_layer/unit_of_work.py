# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from config import DB_USER, DB_PASSWORD, config, DB_HOST, DB_NAME
from adapters import repository
from adapters.repository import user_repository, external_gateway_repository, device_repository, owner_repository, \
    token_repository


class AbstractUnitOfWork(abc.ABC):
    users: repository.AbstractRepository
    external_gateways: repository.AbstractRepository
    devices: repository.AbstractRepository
    owners: repository.AbstractRepository
    used_tokens: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def flush(self):
        self._flush()

    def flush_and_refresh(self, data):
        self._flush_and_refresh(data)

    def collect_new_events(self):
        for user in self.users.seen:
            while user.events:
                yield user.events.pop(0)

        for external_gateway in self.external_gateways.seen:
            while external_gateway.events:
                yield external_gateway.events.pop(0)

        for device in self.devices.seen:
            while device.events:
                yield device.events.pop(0)

        for owner in self.owners.seen:
            while owner.events:
                yield owner.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _flush(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _flush_and_refresh(self, data):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


# DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
#     config.get_postgres_uri(),
#     isolation_level="READ COMMITTED",
# ))

DATABASE_URL = 'mysql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + '/' + DB_NAME
DEFAULT_SESSION_FACTORY_MEMORY = sessionmaker(bind=create_engine(DATABASE_URL))


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY_MEMORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.users = user_repository.UserRepository(self.session)
        self.external_gateways = external_gateway_repository.ExternalGatewayRepository(self.session)
        self.devices = device_repository.DeviceRepository(self.session)
        self.owners = owner_repository.OwnerRepository(self.session)
        self.used_tokens = token_repository.TokenRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def _flush(self):
        self.session.flush()

    def _flush_and_refresh(self, data):
        self.session.flush()
        self.session.refresh(data)

    def rollback(self):
        self.session.rollback()
