from typing import List

from domain.models.user import User


class Owner:
    load_fields = ['id', 'app_identifier']

    def __init__(self, app_identifier: str, configuration=None, users: List[User] = None):
        self.id = None
        self.app_identifier = app_identifier
        self.configuration = configuration
        self.users = users
        self.events = []  # type: List[events.Event]
