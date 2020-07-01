from sqlalchemy import (Table, Column, Integer, String, DateTime, ForeignKey)

from adapters.orm.singleton_meta_data import MetaDataSingleton

app_users = Table(
    'app_users', MetaDataSingleton.get_instance(),
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('app_id', Integer, ForeignKey('owners.id'), nullable=True),
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
