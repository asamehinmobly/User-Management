from sqlalchemy import (Table, Column, Integer, String)

from adapters.orm.singleton_meta_data import MetaDataSingleton

used_token = Table(
    'used_token', MetaDataSingleton.get_instance(),
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('token', String(255), unique=True),
    Column('used', Integer, nullable=True, default=0)
)
