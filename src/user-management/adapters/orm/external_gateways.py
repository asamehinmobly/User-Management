from sqlalchemy import (Table, Column, Integer, String)

from adapters.orm.singleton_meta_data import MetaDataSingleton


external_gateways = Table(
    'external_gateways', MetaDataSingleton.get_instance(),
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('gateway_name', String(255), unique=True),
    Column('app_id', String(255), nullable=True)
)
