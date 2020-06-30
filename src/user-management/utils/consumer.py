from threading import Thread
import pika
from config import BROKER_USERNAME, BROKER_PASSWORD, BROKER_HOST, BROKER_PORT, BROKER_TEMPLATE_JOB_QUEUE, BROKER_VHOST


class ConsumerThread(Thread):
    def __init__(self):
        try:
            super().__init__()
            connection = pika.PlainCredentials(BROKER_USERNAME, BROKER_PASSWORD)
            params = pika.ConnectionParameters(
                credentials=connection,
                host=BROKER_HOST,
                port=BROKER_PORT,
                virtual_host=BROKER_VHOST
            )

            self.conn = pika.BlockingConnection(parameters=params)
            self.ch = self.conn.channel()
            print("Finish init consumer")
        except Exception as e:
            print("Consumer init error {}".format(e))

    def run(self):
        from api.dashboard_api import get_owner_users
        self.ch.queue_declare(BROKER_TEMPLATE_JOB_QUEUE)
        self.ch.basic_consume(get_owner_users, BROKER_TEMPLATE_JOB_QUEUE, True)
        self.ch.start_consuming()
        return
