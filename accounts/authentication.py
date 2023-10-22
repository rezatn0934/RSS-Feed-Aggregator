from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.utils.translation import gettext_lazy as _

from rest_framework import authentication
from rest_framework import exceptions

import jwt
from .utils import decode_jwt
user_model = get_user_model()


class AuthBackend(ModelBackend):
    """
    Custom authentication backend for user authentication.

    This authentication backend allows users to authenticate using their email or username and password.

    Methods:
        authenticate(self, request, username=None, password=None, **kwargs):
            Authenticate a user based on their email or username and password.

        get_user(self, user_id):
            Retrieve a user by their primary key.

    Args:
        request (HttpRequest): The HTTP request object.
        username (str): The email or username used for authentication.
        password (str): The user's password.
        user_id (int): The primary key of the user.

    Returns:
        User: The authenticated user if successful, or None if authentication fails.

    Example Usage:
        This authentication backend is used to authenticate users based on their email or username and password.

    Note:
        - If the user is not found, or if the password is incorrect, authentication will fail.
        - The `get_user` method retrieves the user by their primary key.

    See the Django documentation for more information on custom authentication backends.
    """

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
    """
    Custom authentication class for JSON Web Token (JWT) authentication.

    This authentication class is responsible for authenticating users based on JSON Web Tokens.

    Attributes:
        authentication_header_prefix (str): The expected prefix for the authentication header.
        authentication_header_name (str): The name of the authentication header.

    Methods:
        authenticate_header(self, request):
            Get the authentication header prefix for JWT.

        authenticate(self, request):
            Authenticate a user based on the provided JWT.

        get_payload_from_refresh_token(refresh_token):
            Decode and retrieve the payload from a refresh token.

        get_user_from_payload(payload):
            Retrieve a user based on the payload from a JWT.

        validate_token(payload):
            Validate a JWT token based on its payload and JTI (JSON Token Identifier).

        get_authorization_header(self, request):
            Get the authorization header from the HTTP request.

        check_prefix(self, authorization_header):
            Check if the authorization header includes the expected prefix.

        get_payload_from_access_token(authorization_header):
            Decode and retrieve the payload from an access token.

    Example Usage:
        To use this authentication class, add it to the `DEFAULT_AUTHENTICATION_CLASSES` setting in your
        Django Rest Framework configuration. This class handles the authentication of users based on JWT
        tokens and includes methods for validating, decoding, and verifying the tokens.

    Note:
        - This authentication class relies on the presence of JWT tokens in the authentication header.
        - It also validates the tokens for expiration, signature, and user activation status.

    See the API documentation or authentication settings for more details on usage.
    """

    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def authenticate_header(self, request):
        return self.authentication_header_prefix

    def authenticate(self, request):

        authorization_header = self.get_authorization_header(request)
        if not authorization_header:
            return None

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
                _('Expired token, please login again.'))
        except Exception as e:
            raise exceptions.NotAcceptable(str(e))

    @staticmethod
    def get_user_from_payload(payload):
        user_id = payload.get('user_id')
        if user_id is None:
            raise exceptions.NotFound(_('User id not found'))

        try:
            user = user_model.objects.get(id=user_id)
        except:
            raise exceptions.NotFound(_('User Not Found'))

        if not user.is_active:
            raise exceptions.PermissionDenied(_('User is inactive'))

        return user

    @staticmethod
    def validate_token(payload):
        jti = payload.get('jti')
        if not caches['auth'].keys(jti):
            raise exceptions.PermissionDenied(
                _('Invalid token, please login again.'))

    def get_authorization_header(self, request):
        authorization_header = request.headers.get(self.authentication_header_name)
        if not authorization_header:
            return None
        return authorization_header

    def check_prefix(self, authorization_header):
        prefix = authorization_header.split(' ')[0]
        if prefix != self.authentication_header_prefix:
            raise exceptions.PermissionDenied(_('Token prefix missing'))

    @staticmethod
    def get_payload_from_access_token(authorization_header):
        try:
            access_token = authorization_header.split(' ')[1]
            payload = decode_jwt(access_token)
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.NotAuthenticated(_('Access token expired'))
        except jwt.InvalidSignatureError as e:
            raise exceptions.NotAcceptable(str(e))
        except:
            raise exceptions.ParseError()
