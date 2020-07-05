# from entrypoints.fast_api.request_model.model import
import time

from config import RESET_PASS_TOKEN
from entrypoints.fast_api.request_model.model import UserDataResponse, CreateUserInResponse, UserDataInResponse, \
    SendResetEmailInResponse
from service_layer import unit_of_work
from utils.owner import get_owner_id
from utils.request import check_password, prepare_response_data
from utils.reset_token import create_user_token, encrypt
from utils.subscription import get_user_email_by_order_id, map_plans_data


def check_login(email: str, app_id: int, password: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        user = uow.users.get_by_email(email, app_id)
        if user and check_password(password, user.password):
            return UserDataResponse(email=email, external=user.external, user_id=user.user_id, name=user.name,
                                    id=user.id, province=user.province, active=user.active, app_id=user.app_id,
                                    firebase_id=user.firebase_id, phone=user.phone)
        else:
            raise Exception("Password Incorrect")


def user_create_response(email: str, app_id: int, login_type: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        user = uow.users.get_by_email(email, app_id)

        if user.external:
            external_gateway_conditions = {"id": user.external}
            external_gateways = uow.external_gateways.all(external_gateway_conditions)
            user.external = external_gateways[0].get("gateway_name", None)
        else:
            user.external = "Boltplay"

        time_now = int(time.time())
        user_refresh_token = "%s,%d,%s" % (user.user_id, time_now, get_owner_id(app_id))

        user_response = CreateUserInResponse(
            user_data=UserDataInResponse(
                external=user.external, user_id=user.user_id, name=user.name, id=user.id, province=user.province,
                active=user.active, firebase_id=user.firebase_id, phone=user.phone, app_id=app_id, email=user.email,
                change_pass_time=user.change_pass_time),
            user_token=create_user_token(user),
            refresh_token=encrypt(user_refresh_token)
        )

        return user_response


def reset_password_response(email: str, app_id: int, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        user = uow.users.get_by_email(email)

        user_response = UserDataInResponse(
                external=user.external, user_id=user.user_id, name=user.name, id=user.id, province=user.province,
                active=user.active, firebase_id=user.firebase_id, phone=user.phone, app_id=app_id, email=user.email,
                change_pass_time=user.change_pass_time),

        return user_response


def get_external(uow: unit_of_work.SqlAlchemyUnitOfWork, external_id=None):
    if external_id:
        external_gateway_conditions = {"id": external_id}
        external_gateways = uow.external_gateways.all(external_gateway_conditions)
        return external_gateways[0].get("gateway_name", None)
    else:
        return "Boltplay"


def get_app_users(uow: unit_of_work.SqlAlchemyUnitOfWork, app_id: int, page: int, per_page: int,
                  order: str = None, search_type: str = None, search_keyword: str = None, order_type: str = None):
    keyword = None
    if search_type == "order_id" and search_keyword:
        email = get_user_email_by_order_id(search_keyword)
        search_type = "email"
        if email:
            search_keyword = email
        else:
            search_keyword = "db_has_no_order_id"

    if search_type and search_keyword:
        keyword = {"type": search_type, "keyword": search_keyword}

    if order:
        order_data = {"order": order, "order_type": order_type}
    else:
        order_data = {"order": "creation_on", "order_type": "desc"}

    conditions = {"app_id": app_id, "external": None}
    users = uow.users.all(conditions, page, per_page, keyword, order_data)

    # Get Planes
    if len(users) > 0:
        users = map_plans_data(users)
    users_count = uow.users.count(conditions, keyword)
    returned_data = {'users': users, 'count': users_count}
    return returned_data


def get_external_users(uow: unit_of_work.SqlAlchemyUnitOfWork, app_id: int, user_type: str):
    with uow:
        external_gateway_conditions = {"gateway_name": user_type}
        external_gateways = uow.external_gateways.all(external_gateway_conditions)
        id = external_gateways[0].get("id", None)
        users_conditions = {"app_id": app_id, "external": id}
        users = uow.users.all(users_conditions)
        users_ids = []
        for user in users:
            user_id = user.get("user_id", None)
            user_id = user_id.split(":")[1]
            users_ids.append(user_id)

        return users_ids


def get_count_external_users(uow: unit_of_work.SqlAlchemyUnitOfWork, app_id: int):
    with uow:
        output = []
        conditions = {"app_id": app_id}
        external_gateways = uow.external_gateways.all(conditions)
        for external_gateway in external_gateways:
            users_count_arr = []
            users_count = {}
            gateway_name = external_gateway.get("gateway_name")
            gateway_id = external_gateway.get("id", None)
            users_conditions = {"app_id": app_id, "external": gateway_id}
            count = uow.users.count(users_conditions)
            if count > 0:
                users_count["name"] = gateway_name + " Users"
                users_count["value"] = count
                users_count_arr.append(users_count)
                output.append(users_count_arr)
        return output


def get_user(uow: unit_of_work.SqlAlchemyUnitOfWork, user_id: str, app_id: int):
    conditions = {"user_id": user_id}
    user = uow.users.get(app_id, conditions)
    return user


def get_owners(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        owners = uow.owners.all(condition={})
    return owners
