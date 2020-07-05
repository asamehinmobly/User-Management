
def get_owner_id(app_id):
    from middlewares.oauth_checker import owners
    if isinstance(app_id, str):
        return owners.get(app_id, "")
    elif isinstance(app_id, int):
        for key, value in owners.items():
            if value == app_id:
                return key
        return None
