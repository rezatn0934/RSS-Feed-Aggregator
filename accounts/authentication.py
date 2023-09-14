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

