from threading import Thread
import pika
from config import BROKER_USERNAME, BROKER_PASSWORD, BROKER_HOST, BROKER_PORT, BROKER_EXCHANGE, \
    BROKER_TEMPLATE_JOB_QUEUE, BROKER_VHOST


class ProducerThread(Thread):
    def __init__(self, message=None):
        try:
            super().__init__()

            self.message = message
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
        self.ch.queue_declare(BROKER_TEMPLATE_JOB_QUEUE)
        self.ch.basic_publish(
            exchange=BROKER_EXCHANGE,
            routing_key=BROKER_TEMPLATE_JOB_QUEUE,
            body=self.message
        )
        return
