import pika


class EmailGateway:
    def __init__(self, host=None, port=None, username=None, password=None, vhost=None):
        connection = pika.PlainCredentials(username, password)
        params = pika.ConnectionParameters(
            credentials=connection,
            host=host,
            port=port,
            virtual_host=vhost
        )
        self.conn = pika.BlockingConnection(parameters=params)
        self.ch = self.conn.channel()

    def create_queue(self, name):
        self.ch.queue_declare(name)

    def send(self, message, queue=None, exchange=''):
        '''
        example message (json str):
            {
                "owner_hash": "2108af8fbe137d2181c9d0999b89cd3aa383d968b627c7f17fb6f2dd5a472233",
                "users": [{"name": "Maged", "email": "magedmotawea@gmail.com"}],
                "subject": "expired_coupon"
            }
        '''
        self.create_queue(queue)
        self.ch.basic_publish(
            exchange=exchange,
            routing_key=queue,
            body=message
        )

    # def __del__(self):
    #     self.conn.close()
