from rest_framework.permissions import IsAdminUser, AllowAny

from accounts.authentication import JWTAuthentication


class AuthenticationMixin:
    authentication_classes = (JWTAuthentication, )

    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]
