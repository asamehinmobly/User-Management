# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

from entrypoints.fast_api.request_model.model import CreateUserData, DeviceData


class Command:
    pass


@dataclass
class ResetPassword(Command):
    email: str
    time: datetime


@dataclass
class ChangePassword(Command):
    ID: int
    email: str
    pwd: str
    time: datetime


@dataclass
class CreateUser(Command):
    user_data: CreateUserData
    user_id: int = None
    app_id: str = None


@dataclass
class AttachDeviceToUser(Command):
    device_data: DeviceData


@dataclass
class SendResetEmail(Command):
    email: str
    app_id: int
    token_encoded: str = None


@dataclass
class ResetPassword(Command):
    email: str
    token: str
    new_password: str
    app_id: int


@dataclass
class RefreshToken(Command):
    token: str
    app_id: int


@dataclass
class UpdateDeviceToken(Command):
    device_id: str
    device_token: str


@dataclass
class ExportAppUsers(Command):
    app_id: int = None
    user: dict = None
