from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import caches
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .authentication import AuthBackend, JWTAuthentication
from .mixins import TokenVerificationMixin
from .tasks import send_email_task
from .utils import generate_access_token, generate_refresh_token, jti_maker, publish_event, generate_link
from .serilizers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, PasswordSerializer, \
    ResetPasswordEmailSerializer, PasswordTokenSerializer, ActiveUserSerializer
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
        ser_data.is_valid(raise_exception=True)
        user = ser_data.save()
        active_link = generate_link(request=request, user=user, view_name='accounts:activate-user')
        correlation_id = request.headers.get("correlation-id")

        send_email_task.delay(active_link, user.email, correlation_id)

        device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
        data = {
            'user_id': user.id,
            'data': f'{user.username} has been registered successfully using {device_type}'}

        publish_event(event_type='register', queue_name='register', data=data)
        return Response({'message': _('Registration successful. Please check your email to activate your account.')}, status=status.HTTP_201_CREATED)


class GenerateUserRegisterEmail(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_identifier = serializer.validated_data.get('user_identifier')
        password = serializer.validated_data.get('password')

        user = AuthBackend().authenticate(request, username=user_identifier, password=password)

        if user.is_registered:
            return Response({'message': _("Your account is already active")})

        active_link = generate_link(request=request, user=user, view_name='accounts:activate-user')
        correlation_id = request.headers.get("correlation-id")

        send_email_task.delay(active_link, user.email, correlation_id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

        user = authenticate(request, username=user_identifier, password=password)
        if user is None:
            return Response({'message': _('Invalid Credentials')}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({'message': _("Your account is inactive")}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_registered:
            return Response({'message': _("Your account is not active yet")}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({"message": _("Successful Logout")}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    View for user profile details with retrieval, update, deletion, and password change capabilities.

    This view provides the following actions for managing user profiles:
    - Retrieve: View the user's profile details.
    - Update: Modify the user's profile information.
    - Destroy: Delete the user's account.
    - Change Password: Change the user's password.

    Permissions:
    - IsAuthenticated: Users must be authenticated with a valid access token.
    - UserIsOwner: Users are only allowed to access their own profile.

    Serializer:
    - UserSerializer: Used for viewing and updating the user's profile information.

    Actions:
    - Change Password: An additional custom action to change the user's password.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: A JSON response indicating the result of the requested action along with the appropriate status code.

    Example Usage:
    - Retrieve Profile: GET /api/user-profile/
    - Update Profile: PUT /api/user-profile/
    - Delete Account: DELETE /api/user-profile/
    - Change Password: POST /api/user-profile/change-password/

    Note:
    - The "Change Password" action requires the following data:
      - old_password (str): The user's current password.
      - new_pass (str): The desired new password.

    See the API documentation for more details on each action and its usage.
    """

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
    def change_password(self, request):
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
            return Response({'status': _('password successfully changed')})
        return Response({'error': _('Your old password is wrong')}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPassword(APIView):
    """
    Request a password reset link by providing the user's email.

    Endpoint: POST /api/auth/forget-password/
    Permission: AllowAny (open to all users)

    This view allows users to request a password reset link by providing their email address.

    Args:
        request (HttpRequest): The HTTP request object containing the user's email.

    Returns:
        Response: A JSON response indicating the result of the password reset link request.
    """

    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.get()
            reset_link = generate_link(request=request, user=user, view_name='accounts:change_password_token')
            correlation_id = request.headers.get("correlation-id")

            send_email_task.delay(reset_link, email, correlation_id)
            user = request.user
            device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
            data = {
                'user_id': user.id,
                'data': f'{user.username} has requested for forget password using {device_type}'}

            publish_event(event_type='forget_pass', queue_name='forget_pass', data=data)
            return Response(
                {
                    "message":
                        _("Your password reset password link were emailed")
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": _("User doesn't exists")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordWithToken(TokenVerificationMixin, APIView):
    """
    Change the user's password using a valid token.

    Permission: AllowAny (open to all users)

    This view allows users to change their password by providing a valid token.

    Args:
        request (HttpRequest): The HTTP request object containing the user's new password and token.

    Returns:
        Response: A JSON response indicating the result of the password change.
    """

    serializer_class = PasswordTokenSerializer
    success_message = "Password reset complete"


class ActivateUserWithToken(TokenVerificationMixin, APIView):
    """
    Activate a user's account using a valid token.

    Permission: AllowAny (open to all users)

    This view allows users to activate their account by providing a valid token.

    Args:
        request (HttpRequest): The HTTP request object containing the activation token.

    Returns:
        Response: A JSON response indicating the result of the account activation.
    """

    serializer_class = ActiveUserSerializer
    success_message = "User has been activated successfully"
