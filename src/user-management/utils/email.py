from utils.owner import get_owner_id


def prepare_message_for_email(user, email_type):
    # To integrate with mailchimp
    name = user.get("name", "")
    province = user.get("province", "")
    users_s3_path = None
    if "s3_path" in user:
        users_s3_path = user.pop("s3_path")
    try:
        f_name = name.split()[0]
        province = province if province else ""
    except Exception as e:
        f_name = ""
        province = ""
    user["FNAME"] = f_name
    user["LNAME"] = ""
    user["PROVINCE"] = province

    users_array = [user]
    message = {
        "owner_hash": get_owner_id(user.get("app_id")),
        "users": users_array,
        "subject": email_type,
        "s3_path": users_s3_path
    }
    return message
