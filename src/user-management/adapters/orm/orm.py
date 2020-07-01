import logging
from sqlalchemy import event, MetaData
from sqlalchemy.orm import mapper, relationship
from adapters.orm.owners import owners
from adapters.orm.users import app_users
from adapters.orm.external_gateways import external_gateways
from adapters.orm.devices import user_devices
from adapters.orm.used_tokens import used_token
from domain import model

logger = logging.getLogger(__name__)


def start_mappers():
    logger.info("Starting mappers")
    mapper(model.ExternalGateway, external_gateways)
    mapper(model.UsedToken, used_token)
    devices_mapper = mapper(model.UserDevices, user_devices)
    users_mapper = mapper(model.User, app_users, properties={
        'devices': relationship(devices_mapper)
    })
    mapper(model.Owner, owners, properties={
        'users': relationship(users_mapper, backref="owner")
    })


@event.listens_for(model.User, 'load')
def receive_load(user, _):
    user.events = []


@event.listens_for(model.UserDevices, 'load')
def receive_load(user_devices, _):
    user_devices.events = []
