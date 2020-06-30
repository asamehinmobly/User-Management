# pylint: disable=broad-except, too-many-arguments
import threading
import time
import traceback
from typing import List
from unittest.mock import Mock
import pytest
from skeleton.domain import model
from skeleton.service_layer import unit_of_work
from ..random_refs import random_email

pytestmark = pytest.mark.usefixtures('mappers')


def insert_user(session,user_id, user_email, user_pwd):
    session.execute(
        'INSERT INTO users (ID, email, pwd)'
        ' VALUES (:user_id, :user_email, :user_pwd)',
        dict(user_id=user_id, user_email=user_email, user_pwd=user_pwd)
    )


def get_user_by_email(session, user_email):
    [[user_id]] = session.execute(
        'SELECT ID FROM users'
        ' WHERE email=:user_email',
        dict(user_email=user_email)
    )
    return user_id


def test_change_user_mail_and_get_it(sqlite_session_factory):
    session = sqlite_session_factory()
    user_email = random_email()
    insert_user(session, 'id0100', user_email, "pwd2")
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        user = uow.users.get_by_email(email=user_email)
        user.email = "emad2@inmobly.com"
        uow.commit()

    user_id = get_user_by_email(session, 'emad2@inmobly.com')
    assert user_id == 'id0100'
