import abc
import datetime

from pydantic import ValidationError
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError, DataError
from sqlalchemy.orm import load_only

from domain.models.user import User


class AbstractRepository(abc.ABC):
    Model = None

    def __init__(self):
        self.seen = set()

    def add(self, obj):
        self._add(obj)
        self.seen.add(obj)

    def all(self, condition={}, page=0, per_page=None, keyword=None, order_data=None):
        data = self._all(condition, page, per_page, keyword, order_data)
        if data:
            for item in data:
                self.seen.add(item)
        return self.convert_to_dict(data)

    def convert_to_dict(self, data):
        fields = []
        for row in data:
            out = row.__dict__
            creation_on = out.get("creation_on", None)
            if creation_on:
                out["creation_on"] = out["creation_on"].strftime('%d/%m/%Y')
            if '_sa_instance_state' in out:
                del out['_sa_instance_state']
            fields.append(out)

        return fields

    def get(self, app_id=None, condition=None):
        data = self._get(app_id=app_id, condition=condition)
        if len(data) > 1:
            for item in data:
                self.seen.add(item)
            return data
        else:
            return self.convert_to_dict(data)[0]

    def get_one(self, condition):
        data = self._get_one(condition)
        if data:
            self.seen.add(data)
        return data

    @abc.abstractmethod
    def _add(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_email(self, _email, _app_id) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_id(self, _id) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def _all(self, condition, page, per_page, keyword, order_data):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, app_id=None, condition=None):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_one(self, condition):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, obj):
        self.session.add(obj)

    def _get_by_email(self, _email, _app_id):
        return self.session.query(User).filter_by(email=_email, app_id=_app_id).first()

    def _get_by_id(self, _id: int):
        return self.session.query(User).filter_by(id=_id).first()

    def _all(self, condition, page, per_page, keyword, order_data):
        data = self.session.query(self.Model).filter_by(**condition).options(
            load_only(*self.Model.load_fields))

        if keyword:
            search_type = keyword.get("type", None)
            if search_type == "name":
                data = data.filter(self.Model.name.like("%" + keyword.get("keyword", None) + "%"))
            elif search_type == "email":
                data = data.filter(self.Model.email.like("%" + keyword.get("keyword", None) + "%"))
            elif search_type == "date":
                key = datetime.datetime.strptime(keyword.get("keyword", None), '%d/%m/%Y')
                data = data.filter(
                    self.Model.creation_on.like("%" + key.strftime('%Y-%m-%d') + "%")
                )

        if order_data:
            order_type = order_data.get("order_type")
            order_by = order_data.get("order")
            if order_type == "asc":
                data = data.order_by(asc(order_by))
            else:
                data = data.order_by(desc(order_by))

        if per_page:
            data = data.limit(per_page).offset(page * per_page).all()
        else:
            data = data.all()
        return data

    def _get(self, app_id=None, condition=None):
        if not condition:
            return self.all(app_id)
        data = self.session.query(self.Model).filter_by(**condition).options(
            load_only(*self.Model.load_fields)).all()
        # data = self.convert_to_dict(data)
        return data

    def _get_one(self, condition):
        data = self.session.query(self.Model).filter_by(**condition).options(load_only(*self.Model.load_fields)).first()
        return data

    def _update(self, condition, updated_data):
        try:
            row = self._get_one(condition)
            row.update(updated_data, synchronize_session=False)
            return {'updated': True}
        except SQLAlchemyError as err:
            raise SQLAlchemyError(err)
        except ValidationError as err:
            raise err
        except DataError as err:
            err.message = err.to_primitive()
            raise err
        except Exception as err:
            raise err

    def count(self, condition=None, keyword=None):
        data = self.session.query(self.Model).filter_by(**condition)
        if keyword:
            search_type = keyword.get("type", None)
            if search_type == "name":
                data = data.filter(self.Model.name.like("%" + keyword.get("keyword", None) + "%"))
            elif search_type == "email":
                data = data.filter(self.Model.email.like("%" + keyword.get("keyword", None) + "%"))
            elif search_type == "date":
                key = datetime.datetime.strptime(keyword.get("keyword", None), '%d/%m/%Y')
                data = data.filter(
                    self.Model.creation_on.like("%" + key.strftime('%Y-%m-%d') + "%")
                )
        data = data.count()
        return data
