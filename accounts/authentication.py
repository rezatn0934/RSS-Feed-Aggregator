from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache, caches

from rest_framework import authentication
from rest_framework import exceptions

import jwt
from .utils import decode_jwt
user_model = get_user_model()


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            try:
                user = user_model.objects.get(username=username)
            except user_model.DoesNotExist:
                return None

        return user if (user.check_password(password) and user.is_active) else None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def authenticate_header(self, request):
        return self.authentication_header_prefix

    def authenticate(self, request):

        authorization_header = self.get_authorization_header(request)

        self.check_prefix(authorization_header)

        payload = self.get_payload_from_access_token(authorization_header)
        self.validate_token(payload)

        user = self.get_user_from_payload(payload)

        return user, payload

    @staticmethod
    def get_payload_from_refresh_token(refresh_token):
        try:
            payload = decode_jwt(refresh_token)
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.PermissionDenied(
                'Expired token, please login again.')
        except Exception as e:
            raise exceptions.NotAcceptable(str(e))

    @staticmethod
    def get_user_from_payload(payload):
        user_id = payload.get('user_id')
        if user_id is None:
            raise exceptions.NotFound('User id not found')

        try:
            user = user_model.objects.get(id=user_id)
        except:
            raise exceptions.NotFound('User Not Found')

        if not user.is_active:
            raise exceptions.PermissionDenied('User is inactive')

        return user

    @staticmethod
    def validate_token(payload):
        jti = payload.get('jti')
        if not caches['auth'].keys(jti):
            raise exceptions.PermissionDenied(
                'Invalid token, please login again.')

    def get_authorization_header(self, request):
        authorization_header = request.headers.get(self.authentication_header_name)
        if not authorization_header:
            return None
        return authorization_header

    def check_prefix(self, authorization_header):
        prefix = authorization_header.split(' ')[0]
        if prefix != self.authentication_header_prefix:
            raise exceptions.PermissionDenied('Token prefix missing')

    @staticmethod
    def get_payload_from_access_token(authorization_header):
        try:
            access_token = authorization_header.split(' ')[1]
            payload = decode_jwt(access_token)
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.NotAuthenticated('Access token expired')
        except jwt.InvalidSignatureError as e:
            raise exceptions.NotAcceptable(str(e))
        except:
            raise exceptions.ParseError()
