from adapters.repository.repository import SqlAlchemyRepository
from domain.model import ExternalGateway


class ExternalGatewayRepository(SqlAlchemyRepository):
    Model = ExternalGateway

    def __init__(self, session):
        super().__init__(session)
