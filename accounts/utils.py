import datetime
import random
import string
import uuid

import jwt
from django.conf import settings
from uuid import uuid4

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.publishers import EventPublisher


def generate_access_token(user_id, jti, ttl):
    access_token_payload = {
        "token_type": "access",
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ttl),
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


def jti_maker():
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


def log_entry(request, response, exception=None):
    correlation_id = request.headers.get("correlation-id")
    if not correlation_id:
        correlation_id = uuid.uuid4().hex

    request.META['HTTP_CORRELATION_ID'] = correlation_id

    remote_host = request.META.get('REMOTE_ADDR', '')
    user_id = request.user.id if request.user.is_authenticated else ''
    user_info = {
        'user_id': user_id,
        'user_username': request.user.username if request.user.is_authenticated else '',
        'user_email': request.user.email if request.user.is_authenticated else '',
    }
    request_line = f"{request.method} {request.get_full_path()} HTTP/1.1"
    status_code = response.status_code if not exception else 500
    response_size = response.get('Content-Length', '') if response else ''
    referer = request.META.get('HTTP_REFERER', '') if response else ''
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    elapsed_time = response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
    if status_code == 500:
        message = 'Internal Server Error: An unexpected error occurred while processing the request.'
    else:
        message = str(exception) if exception else 'Request processed successfully'

    if request.resolver_match and request.resolver_match.app_names:
        app_name = request.resolver_match.app_names[0].replace('.', '/')
    else:
        app_name = "unknown_app"

    if request.resolver_match and request.resolver_match.url_name:
        url_name = request.resolver_match.url_name.replace('.', '/')
    else:
        url_name = "unknown_url"

    event = f"Django/api/{app_name}/{url_name}"

    return {
        'correlation_id': correlation_id,
        'remote_host': remote_host,
        'user_info': user_info,
        'request_line': request_line,
        'status_code': status_code,
        'response_size': response_size,
        'referer': referer,
        'user_agent': user_agent,
        'elapsed_time': elapsed_time,
        'message': message,
        'event': event,
    }


def publish_event(event_type, queue_name, data):
    publisher = EventPublisher()
    publisher.publish_event(queue_name=queue_name, event_type=event_type, data=data)
    publisher.close_connection()


def generate_link(request, user, view_name):
    encoded_pk = urlsafe_base64_encode(force_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)

    url = reverse(viewname=view_name, kwargs={"encoded_pk": encoded_pk, "token": token})

    link = f"{request.scheme}://{request.get_host()}{url}"
    return link
