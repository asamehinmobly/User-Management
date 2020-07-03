from datetime import datetime
from typing import List

from domain import events
from domain.models.user_devices import UserDevices


class User:
    load_fields = ['id', 'app_id', 'name', 'email', 'phone', 'user_id', 'firebase_id', 'external', 'active',
                   'change_pass_time', 'creation_on', "province"]

    def __init__(self, app_id: int, name: str, email: str, password: str, phone: str, user_id: str, firebase_id: str,
                 external: str, devices: List[UserDevices]):
        self.id = None
        self.app_id = app_id
        self.name = name
        self.email = email.lower()
        self.password = password
        self.phone = phone
        self.user_id = user_id
        self.firebase_id = firebase_id
        self.external = external
        self.active = 1
        self.devices = devices
        self.province = None
        self.change_pass_time = None
        self.creation_on = self.updated_on = datetime.now()
        self.events = []  # type: List[events.Event]

    def send_reset_password(self):
        self.events.append(events.ResetPasswordEmailSent(
            name=self.name, province=self.province, app_id=self.app_id
        ))

    def reset_password(self):
        self.events.append(events.PasswordChanged(
            name=self.name, province=self.province, app_id=self.app_id
        ))

    def create(self, login_type: str):
        create_status = True
        try:

            self.events.append(events.UserCreated(
                name=self.name, province=self.province, user_id=self.user_id, email=self.email, app_id=self.app_id,
                login_type=login_type
            ))
        except StopIteration:
            create_status = False
            self.events.append(events.LoginFailed(userID=self.ID, date=datetime.utcnow()))
        return create_status
