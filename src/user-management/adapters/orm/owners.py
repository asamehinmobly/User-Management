import sqlalchemy_jsonfield
from sqlalchemy import (Table, Column, Integer, String)

from adapters.orm.singleton_meta_data import MetaDataSingleton

owners = Table(
    'owners', MetaDataSingleton.get_instance(),
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('app_identifier', String(255), unique=True),
    Column('configuration', sqlalchemy_jsonfield.JSONField(enforce_string=False, enforce_unicode=False),
           nullable=False, default="{}")
)
