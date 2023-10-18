from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.cache import caches
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .authentication import AuthBackend, JWTAuthentication
from .tasks import send_email_task
from .utils import generate_access_token, generate_refresh_token, jti_maker, custom_sen_mail, publish_event
from .serilizers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, PasswordSerializer, \
    ResetPasswordEmailSerializer, PasswordTokenSerializer
from .models import User
from .permisions import UserIsOwner
from .publishers import EventPublisher

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
            user = ser_data.save()
            device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
            data = {
                'user_id': user.id,
                'data': f'{user.username} has been registered successfully using {device_type}'}

            publish_event(event_type='register', queue_name='register', data=data)
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

        user = AuthBackend().authenticate(request, username=user_identifier, password=password)
        if user is None:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
        data = {
            'user_id': user.id,
            'data': f'{user.username} has logged in successfully using {device_type}'}
        publish_event(event_type='login', queue_name='login', data=data)

        jti = jti_maker()
        access_token = generate_access_token(user.id, jti, access_token_lifetime)
        refresh_token = generate_refresh_token(user.id, jti, refresh_token_lifetime)

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
        payload = JWTAuthentication.get_payload_from_refresh_token(refresh_token)
        JWTAuthentication.validate_token(payload)

        user = JWTAuthentication.get_user_from_payload(payload)
        jti = payload["jti"]
        caches['auth'].delete(jti)

        jti = jti_maker()
        access_token = generate_access_token(user.id, jti, access_token_lifetime)
        refresh_token = generate_refresh_token(user.id, jti, refresh_token_lifetime)
        caches['auth'].set(jti, user.id)

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
            user = request.user
            device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
            data = {
                'user_id': user.id,
                'data': f'{user.username} has been logout successfully using {device_type}'}

            publish_event(event_type='logout', queue_name='logout', data=data)
            return Response({"message": "Successful Logout"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwner)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.first()
        self.check_object_permissions(self.request, obj)
        return obj

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

            device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
            data = {
                'user_id': user.id,
                'data': f'{user.username} has changed his password using {device_type}'}

            publish_event(event_type='change_pass', queue_name='change_pass', data=data)
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
            user = user.get()

            encoded_pk = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_url = reverse("accounts:change_password_token", kwargs={"encoded_pk": encoded_pk, "token": token})

            reset_link = f"{request.scheme}://{request.get_host()}{reset_url}"
            send_email_task.delay(reset_link, email)
            user = request.user
            device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
            data = {
                'user_id': user.id,
                'data': f'{user.username} has requested for forget password using {device_type}'}

            publish_event(event_type='forget_pass', queue_name='forget_pass', data=data)
            return Response(
                {
                    "message":
                        f"Your password reset password link were emailed"
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordWithToken(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordTokenSerializer

    def patch(self, request, *args, **kwargs):
        """
        Verify token & encoded_pk and then reset the password.
        """
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Password reset complete"}, status=status.HTTP_200_OK)
