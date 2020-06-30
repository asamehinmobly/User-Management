import logging
import sqlalchemy_jsonfield
from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey,
    event, DateTime
)
from sqlalchemy.orm import mapper, relationship

from domain import model

logger = logging.getLogger(__name__)

metadata = MetaData()

app_users = Table(
    'app_users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('app_id', Integer, nullable=True),
    Column('name', String(255)),
    Column('email', String(255)),
    Column('password', String(255)),
    Column('phone', String(255), nullable=True),
    Column('user_id', String(255), unique=True),
    Column('firebase_id', String(255), unique=True),
    Column('external', Integer, nullable=True, default=None),
    Column('active', Integer, nullable=True, default=0),
    Column('creation_on', DateTime, nullable=True),
    Column('updated_on', DateTime, nullable=True),
    Column('change_pass_time', Integer, nullable=True),
    Column('province', String(255), unique=True)
)

user_devices = Table(
    'user_devices', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('app_users.id'), nullable=True),
    Column('device_id', String(255), unique=True),
    Column('device_token', String(255)),
    Column('device_type', String(255)),
    Column('last_login', DateTime, nullable=False)
)

external_gateways = Table(
    'external_gateways', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('gateway_name', String(255), unique=True),
    Column('app_id', String(255), nullable=True)
)

used_token = Table(
    'used_token', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('token', String(255), unique=True),
    Column('used', Integer, nullable=True, default=0)
)

owners = Table(
    'owners', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('app_identifier', String(255), unique=True),
    Column('configuration', sqlalchemy_jsonfield.JSONField(enforce_string=False, enforce_unicode=False),
           nullable=False, default="{}")
)


def start_mappers():
    logger.info("Starting mappers")
    mapper(model.User, app_users)
    mapper(model.ExternalGateway, external_gateways)
    mapper(model.UserDevices, user_devices)
    mapper(model.Owner, owners)
    mapper(model.UsedToken, used_token)


@event.listens_for(model.User, 'load')
def receive_load(user, _):
    user.events = []


@event.listens_for(model.UserDevices, 'load')
def receive_load(user_devices, _):
    user_devices.events = []