from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import AuthBackend, JWTAuthentication
from .utils import generate_access_token, generate_refresh_token, jti_maker
from .serilizers import UserRegisterSerializer, UserLoginSerializer

access_token_lifetime = settings.JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
refresh_token_lifetime = settings.JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()


class UserRegister(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.POST)
        if ser_data.is_valid():
            ser_data.create(ser_data.validated_data)
            return Response(ser_data.data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)

