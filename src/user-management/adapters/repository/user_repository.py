from adapters.repository.repository import SqlAlchemyRepository
from domain import model
from domain.model import User


class UserRepository(SqlAlchemyRepository):
    Model = User

    def __init__(self, session):
        super().__init__(session)

    def get_by_email(self, _email, _app_id) -> model.User:
        user = self._get_by_email(_email, _app_id)
        if user:
            self.seen.add(user)
        return user

