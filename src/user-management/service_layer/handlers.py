# pylint: disable=unused-argument
from __future__ import annotations

import json
import time
from typing import List, Dict, Callable, Type, TYPE_CHECKING

from config import BROKER_TEMPLATE_QUEUE, RESET_PASS_TOKEN
from domain import commands, events, model
from utils.consumer import ConsumerThread
from utils.producer import ProducerThread
from utils.queue import create_queue
from utils.request import prepare_request_data, prepare_response_data, encode_password
from utils.reset_token import create_user_token, encrypt, decrypt
from utils.subscription import set_to_free

if TYPE_CHECKING:
    from adapters import message_broker
    from . import unit_of_work


class InvalidEmail(Exception):
    pass


class InvalidToken(Exception):
    pass


class InvalidPassword(Exception):
    pass


def create_user(cmd: commands.CreateUser, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        user_data = cmd.user_data.__dict__
        user_data["app_id"] = cmd.app_id
        data = prepare_request_data(user_data)
        login_type = data["external"]
        if login_type != "Boltplay":
            # add user as external
            external_gateway_conditions = {"gateway_name": login_type}
            external_gateways = uow.external_gateways.all(external_gateway_conditions)
            data["external"] = external_gateways[0].get("id", None)
        else:
            data["external"] = None

        conditions = {"app_id": data["app_id"], "email": user_data["email"], "external": user_data["external"]}
        users_list = uow.users.all(conditions)

        # Check only in case users are internal
        if len(users_list) > 0 and user_data["external"] is None:
            raise InvalidEmail("Email already exists")

        if users_list:
            user = users_list[0]
        else:
            user = model.User(email=data["email"], password=data["password"], name=data["name"], app_id=data["app_id"],
                              phone=data["phone"], user_id=data["user_id"], firebase_id=data["firebase_id"],
                              external=data["external"])
            uow.users.add(user)
            uow.commit()
        user.create(login_type)
        cmd.user_id = user.id


def attach_device(cmd: commands.AttachDeviceToUser, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        device = model.UserDevices(
            user_id=cmd.device_data.user_id, device_id=cmd.device_data.device_id,
            device_token=cmd.device_data.device_token,
            device_type=cmd.device_data.device_type
        )
        uow.devices.create_or_update(device)
        uow.commit()


def send_reset_email(cmd: commands.SendResetEmail, uow: unit_of_work.AbstractUnitOfWork):
    app_id = cmd.app_id
    with uow:
        expire = int(time.time()) + RESET_PASS_TOKEN
        # Get user data
        user = uow.users.get_by_email(cmd.email, app_id)
        if not user:
            raise InvalidEmail("Email not found")

        token = "RESET_PASS,user_email %s:%d" % (cmd.email, expire)

        token_encoded = encrypt(token)
        if isinstance(user, list):
            for x in user:
                user_data = {
                    "app_id": app_id,
                    "name": x.name,
                    "email": cmd.email, "kwargs": {
                        "token": token_encoded
                    }
                }
                x.send_reset_password()
        else:
            user_data = {
                "app_id": app_id,
                "name": user.name,
                "email": cmd.email, "kwargs": {
                    "token": token_encoded
                }}
            user.send_reset_password()
        cmd.token_encoded = token_encoded
        token = model.UsedToken(token=token_encoded)
        uow.used_tokens.add(token)
        uow.commit()


def reset_password(cmd: commands.ResetPassword, uow: unit_of_work.AbstractUnitOfWork):
    app_id = cmd.app_id
    with uow:
        token = cmd.token
        email = cmd.email
        if token and email:
            new_password = cmd.new_password
            dec_token = decrypt(token).split(':')
            expire_date = int(dec_token[1])
            time_now = int(time.time())
            # check validate Token
            if expire_date < time_now:
                raise InvalidToken("Token invalid")

            # Get User Data
            token_conditions = {"token": token}

            token = uow.used_tokens.get_one(token_conditions)
            if token.used:
                raise InvalidToken("Token invalid")
            else:
                user = uow.users.get_by_email(email, app_id)
                user.password = encode_password(new_password)
                user.change_pass_time = time_now
                uow.users.add(user)
                user.reset_password()

                # save Token To prevent using it again ....
                token.used = 1
                uow.used_tokens.add(token)
                uow.commit()


def refresh_token(cmd: commands.RefreshToken, uow: unit_of_work.AbstractUnitOfWork):
    app_id = cmd.app_id
    with uow:
        returned_data = {}
        token = cmd.token
        token_data = decrypt(token).split(',')
        user_id = token_data[0]
        created_on = int(token_data[1])
        conditions = {"user_id": user_id}
        # Get user data
        user = uow.users.get(app_id, conditions)

        change_pass_on = user.get("change_pass_time", "0")

        if change_pass_on and change_pass_on > created_on:
            raise InvalidPassword("Password Changed")
        else:
            # Create New Token .....
            returned_data["user_token"] = create_user_token(user)
            time_now = int(time.time())
            user_refresh_token = "%s,%d,%s" % (user["user_id"], time_now, user["app_id"])
            returned_data["refresh_token"] = encrypt(user_refresh_token)


def update_device_token(cmd: commands.UpdateDeviceToken, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        device = uow.devices.find_by_device_id(cmd.device_id)
        device.device_token = cmd.device_token
        uow.devices.add(device)
        uow.commit()


def export_app_users(cmd: commands.ExportAppUsers, uow: unit_of_work.AbstractUnitOfWork, data: dict):
    create_queue(app_id=cmd.app_id, user=cmd.user)


def set_user_subscription_to_free(event: events.UserCreated):
    if event.login_type == "Boltplay":
        set_to_free(event)


def send_user_created_notification(event: events.UserCreated, notifications: message_broker.AbstractMessageBroker):
    notifications.send(event.__dict__, "welcome", BROKER_TEMPLATE_QUEUE)


def send_reset_email_notification(event: events.ResetPasswordEmailSent,
                                  notifications: message_broker.AbstractMessageBroker):
    notifications.send(event.__dict__, "reset_password", BROKER_TEMPLATE_QUEUE)


def password_changed_notification(
        event: events.PasswordChanged, notifications: message_broker.AbstractMessageBroker,
):
    notifications.send(event.__dict__, "success_reset_password", BROKER_TEMPLATE_QUEUE)


def login_failed(
        event: events.LoginFailed, uow: unit_of_work.AbstractUnitOfWork
):
    pass  # here you can add history to user


def add_login_history(
        event: events.LoggedIn, uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    pass  # add login history


def publish_loggedin_event(
        event: events.LoggedIn, publish: Callable,
):
    publish('LoggedIn', event)


EVENT_HANDLERS = {
    # events.PasswordChanged: [send_password_changed_notification],
    # events.LoggedIn: [publish_loggedin_event, add_login_history],
    events.UserCreated: [send_user_created_notification],
    events.ResetPasswordEmailSent: [send_reset_email_notification],
    events.PasswordChanged: [password_changed_notification]
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    # commands.ResetPassword: send_reset_password_notification,
    commands.ResetPassword: reset_password,
    commands.CreateUser: create_user,
    commands.AttachDeviceToUser: attach_device,
    # commands.SetUserSubscriptionToFree: set_user_subscription_to_free,
    commands.SendResetEmail: send_reset_email,
    # commands.ExportAppUsers: export_app_users
}  # type: Dict[Type[commands.Command], Callable]
