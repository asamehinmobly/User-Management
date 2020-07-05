import base64
import jwt
from datetime import datetime
import time
from config import JWT_SECRET_KEY, JWT_EXPIRES
from domain.models.user import User
from utils.owner import get_owner_id


def encrypt(plaintext):
    return base64.b64encode(plaintext.encode('UTF-8')).decode('ascii')


def decrypt(ciphertext):
    return base64.b64decode(ciphertext.encode('UTF-8')).decode('ascii')


def create_user_token(user: User):
    app_data = {'app_identifier': get_owner_id(user.app_id)}
    user_dict = user.__dict__
    user_dict.pop('_sa_instance_state', None)
    user_dict.pop("password", None)
    user_dict.pop("creation_on", None)
    user_dict.pop("updated_on", None)
    payload = {
        'exp': datetime.now() + JWT_EXPIRES, 'iat': datetime.now(), 'nbf': datetime.now(),
        'sub': {'user': user_dict, 'application': app_data}
    }
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY)
    return encoded_jwt


def create_refresh_token(user_id, app_id):
    time_now = int(time.time())
    user_refresh_token = "%s,%d,%s" % (user_id, time_now, app_id)
    return encrypt(user_refresh_token)
