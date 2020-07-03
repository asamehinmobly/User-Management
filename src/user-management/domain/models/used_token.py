class UsedToken:
    load_fields = ['id', 'token', 'used']

    def __init__(self, token: str, used: int = 0):
        self.token = token
        self.used = used
