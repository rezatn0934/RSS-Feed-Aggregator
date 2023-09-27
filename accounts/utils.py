import datetime
import random
import string

import jwt
from django.conf import settings
from uuid import uuid4

from django.core.mail import send_mail


def generate_access_token(user_id, jti):
    access_token_payload = {
        "token_type": "access",
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'iat': datetime.datetime.utcnow(),
        'jti': jti,
    }
    access_token = jwt.encode(
        access_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user_id, jti, ttl):
    refresh_token_payload = {
        "token_type": "refresh",
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl),
        'iat': datetime.datetime.utcnow(),
        'jti': jti,

    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return refresh_token


def jti_maker(request, user_id):
    return uuid4().hex


def decode_jwt(token):
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=['HS256'])
    return payload


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def custom_sen_mail(subject, message, receiver):
    recipient_list = [receiver, ]
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, recipient_list)
