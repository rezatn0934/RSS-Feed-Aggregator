from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache

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

        return user if user.check_password(password) else None

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

        refresh_token = request.data.get("refresh_token")

        payload = self.get_payload_from_refresh_token(refresh_token)

        user = self.get_user_from_payload(payload)

        # if jti not in map(lambda x: x.decode("utf8"), redis_instance.keys("*")):
        self.validate_refresh_token(payload)

        authorization_header = self.get_authorization_header(request)

        self.check_prefix(authorization_header)

        payload = self.get_payload_from_access_token(authorization_header)

        return user, payload

    @staticmethod
    def get_payload_from_refresh_token(refresh_token):
        try:
            payload = decode_jwt(refresh_token)
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.PermissionDenied(
                'Expired refresh token, please login again.')
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
    def validate_refresh_token(payload):
        jti = payload.get('jti')
        if jti not in cache:
            raise exceptions.PermissionDenied(
                'Invalid refresh token, please login again.')
