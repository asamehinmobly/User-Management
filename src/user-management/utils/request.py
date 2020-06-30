import time
import uuid
from _sha256 import sha256

from config import OLD_APPS
from utils.reset_token import encrypt


def prepare_request_data(data):
    login_type = data["external"]
    app = OLD_APPS.get(data["app_id"], None)
    if app:
        if login_type == "Boltplay":
            data["user_id"] = data["firebase_id"] = "%s:%s" % (app, encrypt(data["email"]))
        else:
            data["user_id"] = data["firebase_id"] = "%s:%s" % (login_type, data["email"])
    else:
        data["user_id"] = data["firebase_id"] = uuid.uuid4()

    data["password"] = encode_password(data["password"])
    return data


def prepare_response_data(data):
    try:
        data.pop("password", None)
        data.pop("creation_on", None)
        data.pop("updated_on", None)
        data.pop("events", None)
        return data
    except Exception as err:
        print(err.__dict__)
        return None


def encode_password(password):
    return sha256(password.encode('utf-8')).hexdigest()


def check_password(incoming_password, exist_password):
    return True if sha256(incoming_password.encode('utf-8')).hexdigest() == exist_password else False
