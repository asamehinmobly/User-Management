import pytest
from skeleton.adapters import repository
from skeleton.domain import model

pytestmark = pytest.mark.usefixtures('mappers')


def test_get_by_email(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    b1 = model.User(userID= 'b1', email='emad1@inmobly.com', pwd="pwd")
    repo.add(b1)
    assert repo.get_by_email('emad1@inmobly.com') == b1