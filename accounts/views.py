import jwt
from django.conf import settings
from django.core.cache import caches
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet

from .authentication import AuthBackend, JWTAuthentication
from .utils import generate_access_token, generate_refresh_token, jti_maker, get_random_string, custom_sen_mail
from .serilizers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, PasswordSerializer, \
    ResetPasswordEmailSerializer, PasswordTokenSerializer
from .models import User
from .permisions import UserIsOwner

access_token_lifetime = settings.JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
refresh_token_lifetime = settings.JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()


class UserRegister(APIView):
    """
    Register a new user.

    Endpoint: POST /api/auth/register/
    Permission: AllowAny (open to all users)

    This view allows users to register by providing valid user data.

    Args:
        request (HttpRequest): The HTTP request object containing user registration data.

    Returns:
        Response: A JSON response indicating success or failure along with appropriate status codes.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.POST)
        if ser_data.is_valid():
            ser_data.create(ser_data.validated_data)
            return Response(ser_data.data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    Log in an existing user and issue access and refresh tokens.

    Endpoint: POST /api/auth/login/
    Permission: AllowAny (open to all users)

    This view allows users to log in by providing valid credentials (username/email and password).
    It issues an access token and a refresh token upon successful login.

    Args:
        request (HttpRequest): The HTTP request object containing user login data.

    Returns:
        Response: A JSON response containing access and refresh tokens along with appropriate status codes.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_identifier = serializer.validated_data.get('user_identifier')
        password = serializer.validated_data.get('password')
        new_pass = caches['pass'].get(user_identifier)
        if password == new_pass:
            user = User.objects.filter(email=user_identifier)
            if user:
                user = user.get()
                user.set_password(new_pass)
                user.save()

        user = AuthBackend().authenticate(request, username=user_identifier, password=password)
        if user is None:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        jti = jti_maker(request)
        access_token = generate_access_token(user.id, jti)
        refresh_token = generate_refresh_token(user.id, jti, settings.REDIS_CACHE_TTL)

        caches['auth'].set(jti, user.id)

        data = {
            "access": access_token,
            "refresh": refresh_token,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class RefreshToken(APIView):
    """
    Refresh access and refresh tokens.

    Endpoint: POST /api/auth/refresh/
    Permission: IsAuthenticated (requires a valid access token)

    This view allows users to refresh an expired access token by providing a valid refresh token.

    Args:
        request (HttpRequest): The HTTP request object containing the refresh token.

    Returns:
        Response: A JSON response containing new access and refresh tokens along with appropriate status codes.
    """

    permission_classes = []

    def post(self, request):
        refresh_token = request.POST.get("refresh_token").encode("utf-8")
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        user = JWTAuthentication.get_user_from_payload(payload)
        jti = payload["jti"]
        caches['auth'].delete(jti)

        jti = jti_maker(request)
        access_token = generate_access_token(user.id, jti)
        refresh_token = generate_refresh_token(user.id, jti, settings.REDIS_CACHE_TTL)
        caches['auth'].set(jti, user.id, timeout=settings.REDIS_CACHE_TTL, version=None)

        data = {
            "access": access_token,
            "refresh": refresh_token
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    Log out a user by invalidating their token.

    Endpoint: POST /api/auth/logout/
    Permission: IsAuthenticated (requires a valid access token)

    This view allows users to log out by invalidating their token.

    Args:
        request (HttpRequest): The HTTP request object containing the access token.

    Returns:
        Response: A JSON response indicating successful logout or an error message along with appropriate status codes.
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            payload = request.auth
            jti = payload["jti"]
            caches['auth'].delete(jti)

            return Response({"message": "Successful Logout"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwner)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data['old_password']
        new_pass = serializer.validated_data['new_pass']
        if user.check_password(old_password):
            user.set_password(new_pass)
            user.save()
            return Response({'status': 'password successfully changed'})
        return Response({'error': 'Your old password is wrong'}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPassword(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            token = get_random_string(6)
            caches['pass'].set(token, email)
            custom_sen_mail(subject='reset password', message=f'This is your {token}. Use it to change your password',
                            receiver=user.email)
            return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
