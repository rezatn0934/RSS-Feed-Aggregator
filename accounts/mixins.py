from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _


class TokenVerificationMixin:
    """
    A mixin for verifying token and encoded_pk and performing an action with a success message.

    This mixin is designed to be used in Django Rest Framework views for tasks that involve verifying
    tokens and encoded primary keys (encoded_pk), and performing an action with a success message
    upon successful verification.

    Attributes:
        permission_classes (tuple): The permission classes applied to the view.
        success_message (str): The success message to be included in the response upon successful
            verification and action.
        serializer_class (Serializer): The serializer class to validate the data for token and encoded_pk.

    Methods:
        patch(request, *args, **kwargs):
            Verify token and encoded_pk using the provided serializer and perform an action.
            If verification is successful, a response with the success message and status code 200 OK
            is returned.

    Attributes:
        permission_classes = (AllowAny,)
        success_message = None
        serializer_class = None
    """
    permission_classes = (AllowAny,)
    success_message = None
    serializer_class = None

    def patch(self, request, *args, **kwargs):
        """
        Verify token & encoded_pk and then reset the password.
        """
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return Response({"message": self.success_message}, status=status.HTTP_200_OK)
