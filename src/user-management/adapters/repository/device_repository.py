from datetime import datetime
from adapters.repository.repository import SqlAlchemyRepository
from domain.model import UserDevices


class DeviceRepository(SqlAlchemyRepository):
    Model = UserDevices

    def __init__(self, session):
        self.seen = set()
        super().__init__(session)

    def add(self, device: UserDevices):
        self._add(device)
        self.seen.add(device)

    def find_by_device_id(self, device_id):
        data = self.session.query(self.Model).filter(self.Model.device_id == device_id).first()
        return data

    def create_or_update(self, device: UserDevices):
        now = datetime.now()
        exist_device = self.find_by_device_id(device.device_id)
        if not device:
            device.last_login = now
            self.add(device)
        else:
            exist_device.device_token = device.device_token
            exist_device.user_id = device.user_id
            exist_device.last_login = now
            self.add(exist_device)
