import requests
import json

from config import SUBSCRIPTION_BASE_URL


def set_user_subscription_to_free(message, user_data):
    URL = SUBSCRIPTION_BASE_URL + "set_subscription_to_free"
    body = {
        "user_id": user_data.user_id,
        "email": user_data.email,
        "client": user_data.name,
        "user_identity": {
            "province": user_data.province
        },
        "extra": {
            "response": "",
            "hash": "",
            "amount": 0,
            "purchase_token": "",
            "payment_method_token": ""
        }
    }
    headers = {
        "Message": message
    }

    response = requests.post(URL, data=json.dumps(body), headers=headers)

    return response.status_code


def get_user_email(message, order_id):
    try:
        URL = SUBSCRIPTION_BASE_URL + "get_user_management_by_order_id"
        body = {
            "order_id": order_id
        }
        headers = {
            "Message": message
        }
        response = requests.post(URL, data=json.dumps(body), headers=headers)
        if response.status_code == 200:
            output = response.json()
            return output.get("email", None)
        else:
            return None
    except Exception as err:
        return None


def get_users_plans(message, users_id):
    try:
        URL = SUBSCRIPTION_BASE_URL + "get_user_management_subscription_state"
        body = {
            "user_ids": users_id
        }
        headers = {
            "Message": message
        }
        response = requests.post(URL, data=json.dumps(body), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception:
        return []
