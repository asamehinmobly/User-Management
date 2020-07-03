import logging
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship
from adapters.orm.owners import owners
from adapters.orm.users import app_users
from adapters.orm.external_gateways import external_gateways
from adapters.orm.devices import user_devices
from adapters.orm.used_tokens import used_token
from domain.models.external_gateway import ExternalGateway
from domain.models.owner import Owner
from domain.models.used_token import UsedToken
from domain.models.user import User
from domain.models.user_devices import UserDevices

logger = logging.getLogger(__name__)


def start_mappers():
    logger.info("Starting mappers")
    mapper(ExternalGateway, external_gateways)
    mapper(UsedToken, used_token)
    devices_mapper = mapper(UserDevices, user_devices)
    users_mapper = mapper(User, app_users, properties={
        'devices': relationship(devices_mapper)
    })
    mapper(Owner, owners, properties={
        'users': relationship(users_mapper, backref="owner")
    })


@event.listens_for(User, 'load')
def receive_load(user, _):
    user.events = []


@event.listens_for(UserDevices, 'load')
def receive_load(user_devices, _):
    user_devices.events = []
