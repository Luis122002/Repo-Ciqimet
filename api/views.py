from asyncio.log import logger
import http
from django.shortcuts import HttpResponse
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
            odt_instance = form.save()  # Guardar el ODT y obtener la instancia creada
            cant_muestra = form.cleaned_data['Cant_Muestra']
            
            # Crear OTs basados en Cant_Muestra y asociarlos al ODT recién creado
            for _ in range(cant_muestra):
                OT.objects.create(
                    odt=odt_instance,
                    peso_muestra=0.0,  # Valor inicial para peso_muestra
                    volumen=0.0,       # Valor inicial para volumen
                    dilucion=0.0       # Valor inicial para dilucion
                )
            
            return redirect("/ODT")  # Redireccionar a la lista de ODTs (ajusta la URL según tu configuración)
    
    data = {'form': form}
    return render(request, 'Form-ODT.html', data)


def PT_Module(request):

    odts = ODT.objects.all()
    context = {
        'odts': odts
    }

    return render(request, 'ODT-Site.html', context)


def PI_Module(request):

    odts = ODT.objects.all()
    context = {
        'odts': odts
    }

    return render(request, 'ODT-Site.html', context)


def ODT_Info(request):
    if request.method == 'POST':
        odt_id = request.POST.get('odt_id')
        odt = ODT.objects.get(id=odt_id)
        ots = OT.objects.filter(odt=odt)

        context = {
            "odt":odt,
            "ots":ots
        }
        # Puedes hacer más con el ID, como consultas a la base de datos
        return render(request, 'ODT-Info.html', context)
    else:
        # Manejar otros métodos aquí si es necesario
        return HttpResponse(status=405)  # Método no permitido si no es POST
    