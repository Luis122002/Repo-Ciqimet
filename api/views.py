from asyncio.log import logger
import http
import base64
import json
from django.shortcuts import HttpResponse
from django.conf import settings
from django.core import signing
from datetime import datetime, timedelta
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api import models, forms
from django.views.decorators.csrf import csrf_exempt
from .decorators import is_administrador, is_supervisor, is_quimico, is_cliente
from Setup.settings import DEBUG, CORS_ALLOWED_ORIGINS
from django.urls import reverse

def requestAcces(request):
    
    return redirect("/index")

def login(request):

    if DEBUG == True:
        return render(request,"index.html")
    else:
        return redirect()


def Main(request):
    odts = models.ODT.objects.all()
    analisis_list = models.Analisis.objects.all()
    ots = models.OT.objects.all()
    elementos = models.Elementos.objects.all()
    lecturas_elementos = models.LecturasElementos.objects.all()

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

    odts = models.ODT.objects.all()
    context = {
        'odts': odts
    }

    return render(request, 'ODT-Site.html', context)

def AddODT(request):
    form = forms.FormODT()
    if request.method == 'POST':
        form = forms.FormODT(request.POST)
        if form.is_valid():
            odt_instance = form.save()  # Guardar el ODT y obtener la instancia creada
            cant_muestra = form.cleaned_data['Cant_Muestra']
            
            # Crear OTs basados en Cant_Muestra y asociarlos al ODT recién creado
            for _ in range(cant_muestra):
                models.OT.objects.create(
                    odt=odt_instance,
                    peso_muestra=0.0,  # Valor inicial para peso_muestra
                    volumen=0.0,       # Valor inicial para volumen
                    dilucion=0.0       # Valor inicial para dilucion
                )
            
            return redirect("/ODT")  # Redireccionar a la lista de ODTs (ajusta la URL según tu configuración)
    
    data = {'form': form}
    return render(request, 'Form-ODT.html', data)


def PT_Module(request):

    odts = models.ODT.objects.all()
    context = {
        'odts': odts
    }

    return render(request, 'ODT-Site.html', context)


def PI_Module(request):

    odts = models.ODT.objects.all()
    context = {
        'odts': odts
    }

    return render(request, 'ODT-Site.html', context)


def ODT_Info(request):
    if request.method == 'POST':
        odt_id = request.POST.get('odt_id')
        odt = models.ODT.objects.get(id=odt_id)
        ots = models.OT.objects.filter(odt=odt)

        context = {
            "odt":odt,
            "ots":ots
        }
        # Puedes hacer más con el ID, como consultas a la base de datos
        return render(request, 'ODT-Info.html', context)
    else:
        # Manejar otros métodos aquí si es necesario
        return HttpResponse(status=405)  # Método no permitido si no es POST
    



def Elements_Section(request):
    # Obtener todos los elementos
    elementos = models.Elementos.objects.all()
    
    # Obtener tipos únicos para el filtro
    tipos_unicos = models.Elementos.objects.values_list('tipo', flat=True).distinct()

    # Filtrar por tipo si se proporciona en la solicitud
    tipo_filtrado = request.GET.get('tipo', '')
    if tipo_filtrado:
        elementos = elementos.filter(tipo__iexact=tipo_filtrado)

    # Filtrar por estado de habilitación si se proporciona en la solicitud
    enabled_filtrado = request.GET.get('enabled', '')
    if enabled_filtrado:
        if enabled_filtrado.lower() == 'true':
            elementos = elementos.filter(enabled=True)
        elif enabled_filtrado.lower() == 'false':
            elementos = elementos.filter(enabled=False)

    # Manejo de la acción seleccionada
    if request.method == 'POST':
        action = request.POST.get('action', '')
        element_id = request.POST.get('id', '')

        if action and element_id:
            try:
                elemento = models.Elementos.objects.get(pk=element_id)
                if action == 'Activar':
                    elemento.enabled = True
                elif action == 'Desactivar':
                    elemento.enabled = False
                elemento.save()
                return JsonResponse({'success': True})
            except models.Elementos.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Elemento no encontrado'})

    context = {
        'elementos': elementos,
        'tipos_unicos': tipos_unicos,
    }
    return render(request, "Elements.html", context)


def general_form(request, token):
    try:
        # Decodificar el token desde base64
        decoded_data = base64.urlsafe_b64decode(token.encode()).decode()
        data = json.loads(decoded_data)

        target_ID = data.get('id')
        context = data.get('context')
        action = data.get('action')
        stade = data.get('stade')

        form = None
        model = None

        # Verificar el estado
        if stade != "acces":
            return HttpResponseForbidden("Acceso no autorizado.")

        # Validar contexto y acción
        if context not in ['element', 'analytic', 'ODT', 'Read']:
            return HttpResponseForbidden("Contexto no válido.")
        if action not in ['add', 'mod', 'del']:
            return HttpResponseForbidden("Acción no válida.")
        # Procesar según el contexto y la acción
        if context == 'element':
            if action == 'add':
                print(f"Current URL: {request.build_absolute_uri()}")
                form = forms.FormElements()
                if request.method == 'POST':
                    form = forms.FormElements(request.POST)
                    if form.is_valid():
                        form.save()
                        return redirect(reverse('elements_manager'))
            elif action == 'mod':
                # Lógica para modificar un elemento
                model = models.Elementos.objects.get(id=target_ID)
                form = forms.FormElements(instance = model)
                if request.method == 'POST':
                    form = forms.FormElements(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('elements_manager'))
                        
            elif action == 'del':
                model = models.Elementos.objects.get(id=target_ID)
                print(model)
                print(request.method)
                if request.method == "GET":
                    model.delete()
                    print("Deleted")
                    return redirect(reverse('elements_manager'))
        
        elif context == 'analytic':
            # Lógica para 'analytic'
            result_message = f'Análisis {target_ID} procesado con éxito.'
        
        elif context == 'ODT':
            if action == 'add':
                print(f"Current URL: {request.build_absolute_uri()}")
                form = forms.FormODT()
                if request.method == 'POST':
                    form = forms.FormODT(request.POST)
                    if form.is_valid():
                        odt_instance = form.save()  # Guardar el ODT y obtener la instancia creada
                        cant_muestra = form.cleaned_data['Cant_Muestra']
                        
                        # Crear OTs basados en Cant_Muestra y asociarlos al ODT recién creado
                        for _ in range(cant_muestra):
                            models.OT.objects.create(
                                odt=odt_instance,
                                peso_muestra=0.0,  # Valor inicial para peso_muestra
                                volumen=0.0,       # Valor inicial para volumen
                                dilucion=0.0       # Valor inicial para dilucion
                            )
                        return redirect(reverse('Main_ODT'))
            elif action == 'mod':
                # Lógica para modificar un elemento
                model = models.Elementos.objects.get(id=target_ID)
                form = forms.FormElements(instance = model)
                if request.method == 'POST':
                    form = forms.FormElements(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('Main_ODT'))
                        
            elif action == 'del':
                model = models.Elementos.objects.get(id=target_ID)
                print(model)
                print(request.method)
                if request.method == "GET":
                    model.delete()
                    print("Deleted")
                    return redirect(reverse('Main_ODT'))
        
        elif context == 'Read':
            # Lógica para 'Read'
            result_message = f'Lectura {target_ID} procesada con éxito.'


       
        data = {'form':form, 'id':target_ID, "contexModel": context}
        return render(request, "General_form.html", data)

    except Exception as e:
        # En caso de error, retornar una respuesta de error
        return HttpResponseForbidden(f"Error al procesar el token: {str(e)}")
    




def Master_def(request):
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido.")
    
    id = request.POST.get('id')
    context = request.POST.get('context')
    action = request.POST.get('action')
    stade = request.POST.get('stade')

    if stade != "acces":
        return HttpResponseForbidden("Acceso no autorizado.")

    # Crear el objeto de datos
    data = {
        'id': id,
        'context': context,
        'action': action,
        'stade': stade
    }
    
    # Codificar el objeto de datos en base64
    token = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

    print(token)  # Para depuración

    # Crear la URL de redirección
    redirect_url = f'/Action-Resource/{token}/'

    return JsonResponse({'redirect_url': redirect_url, 'message': 'Datos recibidos correctamente'})