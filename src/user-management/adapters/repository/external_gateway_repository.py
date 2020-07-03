from adapters.repository.repository import SqlAlchemyRepository
from domain.models.external_gateway import ExternalGateway


class ExternalGatewayRepository(SqlAlchemyRepository):
    Model = ExternalGateway

    def __init__(self, session):
        super().__init__(session)
