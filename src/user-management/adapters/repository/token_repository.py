from adapters.repository.repository import SqlAlchemyRepository
from domain.model import UsedToken


class TokenRepository(SqlAlchemyRepository):
    Model = UsedToken

    def __init__(self, session):
        super().__init__(session)
