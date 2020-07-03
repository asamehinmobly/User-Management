import abc
import json
from gateway.send_email_gateway import BrokerGateway


class AbstractMessageBroker(abc.ABC):

    @abc.abstractmethod
    def send(self, message, broker_template):
        raise NotImplementedError


class RabbitMessageBroker(AbstractMessageBroker):

    def send(self, message, broker_template):
        try:
            producer = BrokerGateway(message=json.dumps(message), broker_template=broker_template)
            producer.start()

        except Exception as e:
            print(e)
            pass
