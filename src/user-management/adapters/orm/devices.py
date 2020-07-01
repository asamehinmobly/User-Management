from sqlalchemy import (Table, Column, Integer, String, DateTime, ForeignKey)

from adapters.orm.singleton_meta_data import MetaDataSingleton

user_devices = Table(
    'user_devices', MetaDataSingleton.get_instance(),
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('app_users.id'), nullable=True),
    Column('device_id', String(255), unique=True),
    Column('device_token', String(255)),
    Column('device_type', String(255)),
    Column('last_login', DateTime, nullable=False)
)