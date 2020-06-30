from gateway.subscribtion_gateway import set_user_subscription_to_free, get_user_email, get_users_plans
from starlette_context import context


def set_to_free(user_data):
    message = context.data['Message']
    code = set_user_subscription_to_free(message, user_data)
    return code


def get_user_email_by_order_id(order_id):
    print(context)
    message = context.data['Message']
    email = get_user_email(message, order_id)
    return email


def map_plans_data(users):
    message = context.data['Message']
    users_ids = []
    for user in users:
        user_id = user.get("user_id", None)
        users_ids.append(user_id)
    plans = get_users_plans(message, users_ids)
    new_users_data = []
    for user in users:
        user_id = user.get("user_id", None)
        if len(plans) > 0:
            user_plans = plans.get(user_id)
        else:
            user_plans = {}

        user["current_plan"] = user_plans.get("current_plan", None)
        user["expiry_date"] = user_plans.get("expiry_date", None)
        user["next_plan"] = user_plans.get("next_plan", None)
        user["is_free"] = user_plans.get("is_free", None)
        user.pop("app_id", None)
        user.pop("firebase_id", None)

        new_users_data.append(user)
    return new_users_data
