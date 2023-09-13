from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from django.db import models

from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=50, verbose_name=_("Username"), unique=True)
    email = models.CharField(max_length=50,validators=(EmailValidator, ), verbose_name=_("Email"), unique=True)
    first_name = models.CharField(verbose_name=_("First Name"), max_length=50, null=True, blank=True)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name=_("Joined Date"), auto_now_add=True)
    last_modify = models.DateTimeField(verbose_name=_("Last Modify"), auto_now=True)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username
