from adapters.repository.repository import SqlAlchemyRepository
from domain.models.owner import Owner


class OwnerRepository(SqlAlchemyRepository):
    Model = Owner

    def __init__(self, session):
        super().__init__(session)

    def convert_to_dict(self, data):
        owners = {}
        for owner in data:
            owner = owner.__dict__
            if '_sa_instance_state' in owner:
                del owner['_sa_instance_state']
            owners[owner['app_identifier']] = owner['id']
        return owners

    def all(self, condition={}, page=0, per_page=None, keyword=None, order_data=None):
        data = self._all(condition, page, per_page, keyword, order_data)
        return self.convert_to_dict(data)

    def find(self, app_identifier):
        data = self.session.query(self.Model).filter_by(app_identifier=app_identifier).first()
        return data

    def create_or_update(self, app_identifier):
        exist_owner = self.find(app_identifier)
        if not exist_owner:
            new_owner = self.Model(app_identifier=app_identifier, configuration={})
            self.add(new_owner)
            data_obj = new_owner.__dict__
        else:
            data_obj = exist_owner.__dict__

        del data_obj['_sa_instance_state']
        return data_obj
