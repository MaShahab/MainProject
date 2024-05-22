from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenBlacklistView

from accounts import views
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import activateUser, LogoutApiView

app_name = 'accounts'

urlpatterns = [

    # Registration
    path('registration/', views.RegistrationsApiView.as_view(), name='registration'),

    # User activation
    path('confirm/<str:token>/', activateUser, name='user_confirmation'),
    path('activation_link/', views.UserTokenHandle.as_view(), name='activation_link'),


    # Login with token authentication
    # path('login/', ObtainAuthToken.as_view(), name='token_login'),
    path('login/', views.CustomObtainAuthToken.as_view(), name='token_login'),

    # Login with JWT
    # path('jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/create/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('jwt/logout/', LogoutApiView.as_view(), name='token_blacklist'),

    # Logout
    path('logout/', views.CustomDiscardAuthToken.as_view(), name='token_logout'),

    # Change password
    path('change-password/', views.ChangePasswordApiView.as_view(), name='change-password'),

    # Profile
    path('profile/', views.ProfileApiView.as_view(), name='profile'),
]
