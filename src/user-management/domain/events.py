# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from datetime import datetime


class Event:
    pass


@dataclass
class EmailSent(Event):
    name: str
    province: str
    app_id: int


@dataclass
class LoggedIn(Event):
    userID: str
    email: str
    lastLogin: datetime


@dataclass
class PasswordChanged(EmailSent):
    pass


@dataclass
class PasswordChangedFailed(Event):
    userID: int
    email: str
    lastLogin: datetime


@dataclass
class LoginFailed(Event):
    userID: int
    date: datetime


@dataclass
class LoginFailed(Event):
    userID: int
    date: datetime


@dataclass
class SetUserSubscriptionToFree(Event):
    name: str
    email: str
    user_id: str
    province: str


@dataclass
class UserCreated(EmailSent):
    email: str
    user_id: str
    login_type: str


@dataclass
class ResetPasswordEmailSent(EmailSent):
    pass
