from rest_framework import serializers
from .models import User


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
        return User.objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords must match!')
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
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords must match!')
        return attrs


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

