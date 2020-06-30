import uuid


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_prefix():
    return uuid.uuid4().hex[:6]


def random_email(domain=''):
    return f'test.{random_prefix}.@{domain}'
