from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny

from accounts.authentication import JWTAuthentication


class AuthenticationMixin:
    authentication_classes = (JWTAuthentication, SessionAuthentication)

    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_authenticators(self):
        """
        Use SessionAuthentication for 'retrieve' action, in addition to JWTAuthentication.
        """
        if self.request.method in ['POST', 'DELETE']:
            return [JWTAuthentication()]
        return [SessionAuthentication(), JWTAuthentication()]