from django.contrib import admin
from django.urls import path

from apiApp import views
from apiApp.views import test, scrapeTagAddress, multipleRequestScraping

# from apiAPP.views import test2

app_name = 'apiApp'

urlpatterns = [
    path('test', test, name='test'),
    path('white_ip', views.WhiteIPApiView.as_view(), name='white_ip'),
    path('scrape_data/', scrapeTagAddress, name='scrape_api'),
    path('multiple_scrape_data/', multipleRequestScraping, name='multiple_scrape_api'),
    
]
