from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from .models import User
from .utils import publish_event


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        del validated_data['password2']
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(_('Passwords must match!'))
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UserLoginSerializer(serializers.Serializer):
    user_identifier = serializers.CharField()
    password = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    new_pass = serializers.CharField(style={"input_type": "password"}, write_only=True)
    new_pass2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs):
        if attrs['new_pass'] != attrs['new_pass2']:
            raise serializers.ValidationError(_('Passwords must match!'))
        return attrs


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


def validate_password_match(new_pass, new_pass2):
    if new_pass != new_pass2:
        raise serializers.ValidationError(_('Passwords must match!'))


def validate_token_and_encoded_pk(token, encoded_pk):
    if token is None or encoded_pk is None:
        raise serializers.ValidationError(_("Missing data."))


def validate_token(user, token):
    if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError(_("The reset token is invalid"))


def publish_reset_password_event(user, request):
    device_type = request.META.get('HTTP_USER_AGENT', 'UNKNOWN')
    data = {
        'user_id': user.id,
        'data': f'{user.username} has reset his password with a URL link using {device_type}'
    }
    publish_event(event_type='reset_password', queue_name='reset_password', data=data)


class PasswordTokenSerializer(serializers.Serializer):
    new_pass = serializers.CharField(style={"input_type": "password"}, write_only=True)
    new_pass2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs):
        new_pass = attrs.get("new_pass")
        new_pass2 = attrs.get("new_pass2")
        token = self.context.get("kwargs").get("token")
        encoded_pk = self.context.get("kwargs").get("encoded_pk")

        validate_password_match(new_pass, new_pass2)

        pk = urlsafe_base64_decode(encoded_pk).decode()
        user = User.objects.get(pk=pk)

        validate_token_and_encoded_pk(token, encoded_pk)
        validate_token(user, token)

        user.set_password(new_pass)
        user.save()
        request = self.context.get('request')
        publish_reset_password_event(user, request)

        return attrs


class ActiveUserSerializer(serializers.Serializer):
    def validate(self, attrs):
        token = self.context.get("kwargs").get("token")
        encoded_pk = self.context.get("kwargs").get("encoded_pk")

        pk = urlsafe_base64_decode(encoded_pk).decode()
        user = User.objects.get(pk=pk)

        validate_token_and_encoded_pk(token, encoded_pk)
        validate_token(user, token)

        user.is_registered = True
        user.save()

        request = self.context.get('request')
        publish_reset_password_event(user, request)

        return attrs
