from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
import sys
import re

from drf_yasg import openapi

import json

from .serializers import WhiteIpSerializer
from .permissions import IsOwnerOrReadOnly

from rest_framework.decorators import permission_classes

from .models import White_IPs

from django_dump_die.middleware import dump

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import MyQueryParamSerializer
from rest_framework import mixins, viewsets




import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime
import re
import json
from urllib.parse import urlparse

import itertools

# from selenium import webdriver
# from selenium.webdriver.edge.options import Options
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd


# Create your views here.

@api_view(['get', 'post'])
@permission_classes([IsAuthenticated])
def test(request):
    if request.method == 'GET':
        context = {"name": "mahdi", "last_name": "shahabedin"}
        return Response(context)
    elif request.method == 'POST':
        context = {"request method": "post"}
        return Response(context)

    # if request.method == 'get':
    #     context = {"name": "mahdi", "last_name": "shahabedin"}
    #     return Response(context)

# class ScrapeData(APIView):

#     permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

#     def get(self, request):
#         product = Products.objects.all()
#         serializer = ProductSerializer(product, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         pass

def validate_ip(ip_str):
    reg = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    if re.match(reg, ip_str):
        return True
    else:
        return False

class WhiteIPApiView(APIView):
    serializer_class = WhiteIpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ips = White_IPs.objects.all()
        return ips
    
    def get_spcIP(self,user_id):
        spc_ip = White_IPs.objects.filter(ip=user_id)
        return spc_ip

    def get(self, request, *args, **kwargs):

        try:
            if request.data['ip'] != None:
                ip = request.data['ip']
                ip_obj = self.get_spcIP(ip)
                serializer = WhiteIpSerializer(ip_obj,many=True)
                return Response(serializer.data[0])
            else:
                pass
                
        except Exception as e:
                # return Response({"ababababab":request.data})
                ip_list = self.get_queryset()
                serializer = WhiteIpSerializer(ip_list,many=True)
                return Response(serializer.data)

    def post(self,request, *args, **kwargs):
        try:
            serializer = WhiteIpSerializer(data=request.data)
            if serializer.is_valid() and validate_ip(request.data['ip']) == True:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors)
        
        except Exception as e:
            return Response({"Error":str(e)})
        
    def put(self,request, *args, **kwargs):
        try:
            # return Response(request.data['id'])
            white_ip = White_IPs.objects.get(id=int(request.data['id']))
            serializer = WhiteIpSerializer(white_ip, data=request.data)
            if serializer.is_valid():
                serializer.save()
                a = {}
                a['details'] = 'white_ip successfully updated'
                a['payload'] = serializer.data
                return Response(a, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(serializer.errors())
        except Exception as e:
            return Response({"Error":str(e)})
        
    def delete(self,request, *args, **kwargs):
        try:
            white_ip = White_IPs.objects.get(id=int(request.data['id']))
            white_ip.delete()
            return Response({"details": "ip address is successfully deleted!"})
        except Exception as e:
            return Response({"Error":str(e)})



def requestScraping(input_parameters):

    link_url = input_parameters['link_url']
    tag_address = input_parameters['tag_address']

    # return tag_address

    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(link_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    element_instance = soup.select(tag_address)
        
    global final_value

    if len(element_instance) == 1:
        final_value = element_instance[0].text.strip()
    elif len(element_instance) > 1:
        value_list = []
        for value in element_instance:
            value_list.append(value.text.strip())
        final_value = value_list

    return(final_value)

    

@swagger_auto_schema(request_body=MyQueryParamSerializer, method='post')
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def scrapeTagAddress(request):

    try:
        if 'link_url' in request.data and 'tag_address' in request.data:
            # print("salam")
            output = {}
            output['OK'] = True
            output['Link Url'] = request.data['link_url']
            output['Tag Address'] = request.data['tag_address']
            output['Result'] = requestScraping(request.data)
            return Response(output, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Both parameters (link_url & tag_address) must be passed as inputs"})

    except Exception as e:
            return Response({"Error":"Could not find input tag address in input web url."}, status=status.HTTP_404_NOT_FOUND)
            # return Response({"Error":str(e)})


