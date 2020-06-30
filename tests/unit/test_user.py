from datetime import date, timedelta
from domain import events
from domain.model import User

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_login():
    user = User(userID="asd", email="asd@asd.com", pwd="asd")
    result = user.login("asd")
    assert result == True


def test_change_password():
    user = User(userID="asd", email="asd@asd.com", pwd="asd")
    user.change_password("qwe")
    result = user.login("qwe")
    assert result == True
