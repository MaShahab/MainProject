from django.shortcuts import redirect
from django_dump_die.middleware import dump
from rest_framework import generics
from rest_framework.decorators import api_view

from .serializers import (
    RegistrationSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    CustomAuthTokenSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from mainApp.models import Profile
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

User = get_user_model()


class RegistrationsApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "Dear user your account is created and now you are capable to login on service",
                "email": serializer.validated_data["email"],
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    # noinspection PyAttributeOutsideInit
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"details": "password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class UserTokenHandle(generics.GenericAPIView):

    # noinspection PyAttributeOutsideInit
    def get(self, request, *args, **kwargs):

        self.email = "mahshahab@gmail.com"
        user_object = get_object_or_404(User, email=self.email)
        token = self.get_token_for_user(user_object)
        return redirect(reverse("accounts:user_confirmation", kwargs={"token": token}))

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class LogoutApiView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            serializer = self.serializer_class(data = request.data)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            return Response({"details": "refresh token successfully blacklisted"}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({"Error": "Input refresh token is not valid"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    



@api_view(("GET",))
def activateUser(request, token):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
        user_obj = User.objects.get(id=user_id)

        if user_obj.is_verified:
            return Response({"details": "Your account already activated"})
        else:
            user_obj.is_verified = True
            user_obj.save()
            return Response(
                {"details": "Dear user, your account is activated successfully"}
            )
    except ExpiredSignatureError:
        return Response(
            {"details": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST
        )
    except InvalidSignatureError:
        return Response(
            {"details": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
        )
