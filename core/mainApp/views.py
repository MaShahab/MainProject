from django.shortcuts import render
from django_dump_die.middleware import dump

def test(request):
    dump("salam")

