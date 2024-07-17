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
from api.models import User, ODT, Analisis, OT, Elementos, LecturasElementos
from api.forms import FormODT
from django.views.decorators.csrf import csrf_exempt
from .decorators import is_administrador, is_supervisor, is_quimico, is_cliente
from Setup.settings import DEBUG, CORS_ALLOWED_ORIGINS

def login(request):

    if DEBUG == True:
        return render(request,"index.html")
    else:
        return redirect()


def Main(request):
    odts = ODT.objects.all()
    analisis_list = Analisis.objects.all()
    ots = OT.objects.all()
    elementos = Elementos.objects.all()
    lecturas_elementos = LecturasElementos.objects.all()

    # Pasar los datos al contexto de la plantilla
    context = {
        'odts': odts,
        'analisis_list': analisis_list,
        'ots': ots,
        'elementos': elementos,
        'lecturas_elementos': lecturas_elementos
    }
    
    return render(request, 'index.html', context)
       
    

def ODT_Module(request):

    odts = ODT.objects.all()
    context = {
        'odts': odts
    }

    return render(request, 'ODT-Site.html', context)

def AddODT(request):

    form = FormODT()
    if request.method == 'POST':
        form = FormODT(request.POST)
        if form.is_valid():
            form = form.save()
            return redirect("/api/ODT")
    data = {'form':form}
    return render(request, 'Form.html', data)

    