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
import socket

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


from collections import ChainMap




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
# from msedge.selenium_tools import EdgeOptions
# from msedge.selenium_tools import Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

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



def checkIPValidation(ip):
    ips_objects = White_IPs.objects.all()
    ips_array = []
    for value in ips_objects:
        ips_array.append(value.ip)

    if ip in ips_array: 
        return True 
    else: 
        return False




def requestScraping(input_parameters):

    link_url = input_parameters['link_url']
    tag_address = input_parameters['tag_address']

    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(link_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    element_instance = soup.select(tag_address)
    # return str(element_instance)

    if len(element_instance) == 1:
        return str(element_instance[0].text.strip())
    elif len(element_instance) > 1:
        value_list = []
        for value in element_instance:
            value_list.append(value.text.strip())
        return value_list

    

@swagger_auto_schema(request_body=MyQueryParamSerializer, method='post')
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def scrapeTagAddress(request):

    try:
        if 'link_url' in request.data and 'tag_address' in request.data:
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

@swagger_auto_schema(request_body=MyQueryParamSerializer, method='post')
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def multipleRequestScraping(request):
    # hostname = socket.gethostname()
    # IPAddr = socket.gethostbyname(hostname)
    # return Response(checkIPValidation("195.248.242.169"))
    try:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        if checkIPValidation(IPAddr) == False:
            inputs = request.data['inputs']
            parameters_list = []
            for parameter in inputs:
                output = {}
                if 'link_url' in parameter and 'tag_address' in parameter:
                    output['OK'] = True
                    output['Link Url'] = parameter['link_url']
                    output['Tag Address'] = parameter['tag_address']
                    output['Result'] = requestScraping(parameter)
                else:
                    output['OK'] = False
                    output['parameter'] = parameter
                    output['error'] = "Both parameters (link_url & tag_address) must be passed as inputs"
                parameters_list.append(output)

            return Response(parameters_list)
        elif checkIPValidation(IPAddr) == True:
            return Response({"response": "You don't have permission to call this method"})
    
    except Exception as e:
            return Response({"Error":"Could not find input tag address in input web url."}, status=status.HTTP_404_NOT_FOUND)
            # return Response({"Error":str(e)})
            


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

def merge_dicts(dicts_array):
    return dict(ChainMap(*dicts_array))





def scrapeMultiDataWithSelenium(request,input_data):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        from selenium_stealth import stealth
        import undetected_chromedriver as uc

        import os

        chrome_options = Options()
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument("--headless=new")
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # chrome_options.add_argument('start-maximized')
        # os.environ['WDM_SSL_VERIFY'] = '0' #Disable SSL

        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('start-maximized')
        chrome_options.add_argument('enable-automation')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/96.0.4664.110 Safari/537.36")
        

        driver = webdriver.Remote(command_executor='http://chrome:4444/wd/hub',desired_capabilities=DesiredCapabilities.CHROME,options=chrome_options)

        url = input_data['link_url']
        driver.get(url)

        if 'click_items' in input_data:
            click_items = input_data['click_items']
            for click_item in click_items:
                element_to_click = driver.find_element(By.CSS_SELECTOR, click_item)
                print(element_to_click.text)
                element_to_click.click()


        html = driver.page_source
        soup = BeautifulSoup(html)

        if 'link_url' in input_data and 'tag_addresses' in input_data:
            link_url = input_data['link_url']
            tag_addresses = input_data['tag_addresses']

            final_values_list = []
            response = {}

            for tag_addresse in tag_addresses:
                # value = []
                value = {}
                element_instance = soup.select(tag_addresse)

                if len(element_instance) == 1:
                    value[tag_addresse] = str(element_instance[0].text.strip())
                elif len(element_instance) > 1:
                    value_list = []
                    for elemnent in element_instance:
                        value_list.append(elemnent.text.strip())
                    value[tag_addresse] = value_list
                    # value = value_list

                else:
                    value[tag_addresse] = "Null"

                final_values_list.append(value)
            # return Response(final_values_list)
            
            merged_values_dict = merge_dicts(final_values_list)

            # return Response(final_values_list)
            response['values'] = merged_values_dict
        else:
            return Response({"error":"Both parameters (link_url & tag_address) must be passed as inputs"})
        
        if 'attributes' in input_data:
            attributes = request.data['attributes']
            attributes_keys = list(attributes.keys())

            # print(attributes_keys)

            my_list = []
            a = []
            b = []
            final_attr_values = []
            global x

            my_dict = {}
            for attribute_key in attributes_keys:
                spc_attribute_parameters = request.data['attributes'][attribute_key]

                
                for spc_attribute_parameter in spc_attribute_parameters:
                    final_attr_values.append(spc_attribute_parameter)
                    try:
                        my_value = soup.select_one(attribute_key)[spc_attribute_parameter]
                        # print(my_value.text.strip())
                        b.append({spc_attribute_parameter:my_value})
                    except:
                        b.append({spc_attribute_parameter:"Null"})
                my_value = []
                a.append(attribute_key)
                a.append(b)
                b = []
                final_attr_values = []

            




            z = int(len(a))/2
            z = int(z)
            h = split_list(a, wanted_parts=z)

            z_dict = {}
            for l in h:
                super_dict = {key:val for d in l[1] for key,val in d.items()}
                z_dict[l[0]] = super_dict

            response['attributes'] = z_dict

        # return Response(vv)
        driver.quit()
        return Response(response)

        

       
    except Exception as e:
            # return Response({"Error":"Could not find input tag address in input web url."}, status=status.HTTP_404_NOT_FOUND)
            driver.quit()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return Response({"Error":str(e) + 'in line ' + str(exc_tb.tb_lineno)})

    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # example
    # driver = webdriver.Remote("http://127.0.0.1:4444", options=options)

    # sleep(5)
    # driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/',desired_capabilities=DesiredCapabilities.CHROME)


    # print(input_data['link_url'])
    # a = input_data['link_url']
    # return a

    # edge_options = EdgeOptions()
    # edge_options.use_chromium = True
    # driver = Edge(executable_path='D:/pythonProjects/edgedriver_win64/msedgedriver.exe', options=edge_options)
    # driver.get(link)

    # timeout = 2
    # try:
    #     element_present = EC.presence_of_element_located((By.ID, 'obituariesResults'))
    #     WebDriverWait(driver, timeout).until(element_present)
    #     obituaries = driver.find_elements_by_class_name("obit-result-container.component.screen-title.screen-title-split-left")
    # except TimeoutException:
    #         print("Timed out waiting for page to load")
    



@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def scrapeMultiData(request):
    try:
        global value
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        if checkIPValidation(IPAddr) == False:
            input_data = request.data

            # r2 = requests.get('www.localhost:4444/')
            # b_soup2 = BeautifulSoup(r2.text, 'html.parser')
            # chrome_driver_ip2 = b_soup2.find("div",{"class":"MuiGrid-root"})
            # print(chrome_driver_ip2)
            # r2.close()

            if 'is_selenium' not in input_data or input_data['is_selenium'] == 'false':

                if 'link_url' in input_data and 'tag_addresses' in input_data:
                    link_url = input_data['link_url']
                    tag_addresses = input_data['tag_addresses']
                    headers = {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                    r = requests.get(link_url, headers=headers)
                    soup = BeautifulSoup(r.text, 'html.parser')

                    final_values_list = []
                    response = {}

                    for tag_addresse in tag_addresses:
                        # value = []
                        value = {}
                        element_instance = soup.select(tag_addresse)

                        if len(element_instance) == 1:
                            value[tag_addresse] = str(element_instance[0].text.strip())
                        elif len(element_instance) > 1:
                            value_list = []
                            for elemnent in element_instance:
                                value_list.append(elemnent.text.strip())
                            value[tag_addresse] = value_list
                            # value = value_list

                        else:
                            value[tag_addresse] = "Null"

                        final_values_list.append(value)
                    # return Response(final_values_list)
                    
                    merged_values_dict = merge_dicts(final_values_list)

                    # return Response(final_values_list)
                    response['values'] = merged_values_dict
                else:
                    return Response({"error":"Both parameters (link_url & tag_address) must be passed as inputs"})
                
                if 'attributes' in input_data:
                    attributes = request.data['attributes']
                    attributes_keys = list(attributes.keys())

                    my_list = []
                    a = []
                    b = []
                    final_attr_values = []
                    global x

                    my_dict = {}
                    for attribute_key in attributes_keys:
                        spc_attribute_parameters = request.data['attributes'][attribute_key]
                        
                        for spc_attribute_parameter in spc_attribute_parameters:
                            final_attr_values.append(spc_attribute_parameter)
                            try:
                                my_value = soup.select_one(attribute_key)[spc_attribute_parameter]
                                b.append({spc_attribute_parameter:my_value})
                            except:
                                b.append({spc_attribute_parameter:"Null"})
                        my_value = []
                        a.append(attribute_key)
                        a.append(b)
                        b = []
                        final_attr_values = []




                    z = int(len(a))/2
                    z = int(z)
                    h = split_list(a, wanted_parts=z)

                    z_dict = {}
                    for l in h:
                        super_dict = {key:val for d in l[1] for key,val in d.items()}
                        z_dict[l[0]] = super_dict

                    response['attributes'] = z_dict

                # return Response(vv)
                return Response(response)     
            

            elif input_data['is_selenium'] == 'true':
                bb = scrapeMultiDataWithSelenium(request,input_data)
                # print(bb)
                # return Response({"response": bb})
                return bb


        elif checkIPValidation(IPAddr) == True:
            return Response({"response": "You don't have permission to call this method"})
        

    except Exception as e:
            # return Response({"Error":"Could not find input tag address in input web url."}, status=status.HTTP_404_NOT_FOUND)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return Response({"Error":str(e) + " in line "+ str(exc_tb.tb_lineno)})


