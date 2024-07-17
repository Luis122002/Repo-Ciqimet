from asyncio.log import logger
import http
from django.conf import settings
from django.core import signing
from datetime import datetime, timedelta
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import User
from django.views.decorators.csrf import csrf_exempt
from .decorators import is_administrador, is_supervisor, is_quimico, is_cliente
from Setup.settings import DEBUG, CORS_ALLOWED_ORIGINS

def login(request):

    if DEBUG == True:
        return render(request,"index.html")
    else:
        return redirect()


def Main(request):
    if settings.DEBUG:
        return render(request, "index.html")
    else:
        return redirect(settings.CORS_ALLOWED_ORIGINS[0])
       
    

def ODT_Module(request):
    return render
    