from abc import ABC

from rest_framework import serializers
from mainApp.models import User, Profile
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework.serializers import (CharField)

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.contrib.auth import authenticate

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    password1 = CharField(label='Confirm Password', write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password1']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password1'):
            raise serializers.ValidationError(
                {'detail': 'password doesnt match'}
            )
        validate_password(attrs.get('password'))
        # try:
        #     validate_password(attrs.get('password1'))
        # except exceptions.ValidationError as e:
        #     raise serializers.ValidationError({'password': list(e.message)})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password1', None)
        return super().create(validated_data)


# noinspection PyAbstractClass
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label="Email", write_only=True
    )
    password = serializers.CharField(
        label="Password", write_only=True, style={'input_type': 'password'}, trim_whitespace=False
    )
    token = serializers.CharField(
        label="Token", read_only=True
    )

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)

            if not user:
                msg = 'unable to login with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_verified:
                raise serializers.ValidationError({"details": "user is not verified"}, code='authorization')
        else:
            msg = 'Must include username and password'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


# noinspection PyAbstractClass
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        auth_dict = {}
        auth_dict['access_token'] = validated_data['access']
        auth_dict['refresh_token'] = validated_data['refresh']
        payload_dict = {}
        payload_dict['message'] = 'You are successfully authenticated'
        payload_dict['email'] = self.user.email
        data = {}
        data['Authentication'] = auth_dict
        data['Payload'] = payload_dict
        return data


# noinspection PyAbstractClass
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password1'):
            raise serializers.ValidationError(
                {'detail': 'password doesnt match'}
            )
        validate_password(attrs.get('new_password'))
        # try:
        #     validate_password(attrs.get('password1'))
        # except exceptions.ValidationError as e:
        #     raise serializers.ValidationError({'password': list(e.message)})

        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'email', 'first_name', 'last_name', 'image', 'description')
        read_only_fields = ['email']


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self,**kwargs):
        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad token')

