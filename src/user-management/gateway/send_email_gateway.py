from threading import Thread

import pika

from config import BROKER_USERNAME, BROKER_PASSWORD, BROKER_PORT, BROKER_HOST, BROKER_VHOST, BROKER_TEMPLATE_JOB_QUEUE, \
    BROKER_EXCHANGE


class BrokerGateway(Thread):
    def __init__(self, broker_template, message=None):
        try:
            super().__init__()

            self.message = message
            self.broker_template = broker_template
            connection = pika.PlainCredentials(BROKER_USERNAME, BROKER_PASSWORD)
            params = pika.ConnectionParameters(
                credentials=connection,
                host=BROKER_HOST,
                port=BROKER_PORT,
                virtual_host=BROKER_VHOST
            )

            self.conn = pika.BlockingConnection(parameters=params)
            self.ch = self.conn.channel()
            print("Finish init producer")
        except Exception as e:
            print("Producer init error {}".format(e))

    def run(self):
        self.ch.queue_declare(self.broker_template)
        self.ch.basic_publish(
            exchange=BROKER_EXCHANGE,
            routing_key=self.broker_template,
            body=self.message
        )
        return

    # def __init__(self, host=None, port=None, username=None, password=None, vhost=None):
    #     super().__init__()
    #     connection = pika.PlainCredentials(username, password)
    #     params = pika.ConnectionParameters(
    #         credentials=connection,
    #         host=host,
    #         port=port,
    #         virtual_host=vhost
    #     )
    #     self.conn = pika.BlockingConnection(parameters=params)
    #     self.ch = self.conn.channel()
    #
    # def create_queue(self, name):
    #     self.ch.queue_declare(name)
    #
    # def send(self, message, queue=None, exchange=''):
    #     '''
    #     example message (json str):
    #         {
    #             "owner_hash": "2108af8fbe137d2181c9d0999b89cd3aa383d968b627c7f17fb6f2dd5a472233",
    #             "users": [{"name": "Maged", "email": "magedmotawea@gmail.com"}],
    #             "subject": "expired_coupon"
    #         }
    #     '''
    #     self.create_queue(queue)
    #     self.ch.basic_publish(
    #         exchange=exchange,
    #         routing_key=queue,
    #         body=message
    #     )
    #
    # # def __del__(self):
    # #     self.conn.close()
