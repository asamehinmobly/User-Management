import json
import logging
import redis

from skeleton import bootstrap, config
from skeleton.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info('Redis pubsub starting')
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('change_password')

    for m in pubsub.listen():
        handle_password_changed(m, bus)


def handle_password_changed(m, bus):
    logger.info('handling %s', m)
    data = json.loads(m['data'])


if __name__ == '__main__':
    main()
