import json
from http import HTTPStatus

from starlette.responses import Response

from utils.consumer import ConsumerThread
from utils.producer import ProducerThread


def create_queue(app_id, user):
    try:
        producer = ProducerThread(message=json.dumps({"app_id": app_id, "user": user}))
        producer.start()
        consumer = ConsumerThread()
        consumer.start()
        return Response(content=json.dumps({"status": True}), status_code=HTTPStatus.OK.value,
                        media_type='application/json')
    except Exception as e:
        if 'message' not in e.__dict__:
            e.message = repr(e)
        return Response(content=json.dumps({"errors": e.message}), status_code=HTTPStatus.BAD_REQUEST.value,
                        media_type='application/json')
