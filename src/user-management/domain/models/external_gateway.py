class ExternalGateway:
    load_fields = ['id', 'gateway_name']

    def __init__(self, gateway_name: str, app_id: str):
        self.gateway_name = gateway_name
        self.app_id = app_id
        self.events = []  # type: List[events.Event]

