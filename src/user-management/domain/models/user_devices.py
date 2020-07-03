from datetime import datetime


class UserDevices:

    def __init__(self, user_id: int, device_id: str, device_token: str, device_type: str, last_login: datetime = None):
        self.user_id = user_id
        self.device_id = device_id
        self.device_token = device_token
        self.device_type = device_type
        self.last_login = last_login
        self.events = []  # type: List[events.Event]
