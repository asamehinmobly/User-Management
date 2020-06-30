import json
from http import HTTPStatus
from fastapi import Response
import binascii
import base64
from Crypto.Cipher import AES
from Crypto.Util import Counter
from starlette.requests import Request

import views
from config import API_GATEWAY_KEY, IV
from utils.bus_singleton import BusSingleton

owners = views.get_owners(uow=BusSingleton.get_instance().uow)


class OauthChecker:
    def __init__(self, auth: bool = True, auth_type: str = "admin"):
        self.auth = auth
        self.auth_type = auth_type

    def __call__(self, request: Request):
        if self.auth:
            message = request.headers.get('Message')
            dec_message = decrypt_message(message)
            b = str(dec_message, encoding="utf-8")
            credentials_dict = json.loads(b)

            if credentials_dict:
                app_id = credentials_dict['application']['app_identifier']
                if app_id in owners:
                    app_id = owners[app_id]
                else:
                    new_owner = BusSingleton.get_instance().uow.owners.create_or_update(app_id)
                    app_id = new_owner['app_identifier']
                user = credentials_dict.get('user', None)

                if self.auth_type == "admin":
                    response = {"app_id": app_id, "user": user}
                else:
                    try:
                        user_id = credentials_dict['user']['user_id']
                        change_pass_time = credentials_dict['user']['change_pass_time']
                        response = {"app_id": app_id, "user_id": user_id, "change_pass_time": change_pass_time}
                    except Exception:
                        return response_with_invalid()
                return response
            else:
                return response_with_unauthorized()


def int_of_string():
    ivByte = bytes(IV, encoding="utf8")
    return int(binascii.hexlify(ivByte), 16)


def decrypt_message(message):
    message = base64.b64decode(message)
    ctr = Counter.new(128, initial_value=int_of_string())
    aes = AES.new(API_GATEWAY_KEY, AES.MODE_CTR, counter=ctr)
    dec_msg = aes.decrypt(message[0:])
    b = str(dec_msg, encoding="utf-8")
    payload = base64.b64decode(b)
    return payload


def response_with_unauthorized():
    return Response(content=json.dumps({'error': 'UNAUTHORIZED TOKEN'}),
                    status_code=HTTPStatus.UNAUTHORIZED.value, media_type="application/json")


def response_with_valid():
    return Response(content=json.dumps({'error': 'UNAUTHORIZED TOKEN'}),
                    status_code=HTTPStatus.OK.value, media_type="application/json")


def response_with_invalid():
    return Response(content=json.dumps({'error': 'UNAUTHORIZED TOKEN'}),
                    status_code=HTTPStatus.FORBIDDEN.value, media_type="application/json")
