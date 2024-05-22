from django.contrib import admin
from django.urls import path
from mainApp.views import test
# from mainApp.views import test, hello, formTest, formFunction

urlpatterns = [
    path('test', test, name='test'),
]