import datetime
import jwt
from django.conf import settings
from uuid import uuid4


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
    return f"{uuid4().hex} || {user_id} || {request.META['HTTP_USER_AGENT']} || {request.META['USERNAME']}"

