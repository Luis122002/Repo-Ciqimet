from asyncio.log import logger
import http
import base64
import json
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.core import signing
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login
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
from django.db import IntegrityError, transaction
from django.db.models import Q

@login_required(login_url='/login/')
def requestAcces(request):
    return redirect("/index")


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/index')
    else:
        form = AuthenticationForm()
    
    return render(request, "login.html", {'form': form})

@login_required(login_url='/login/')
def Main(request):
    odts = models.ODT.objects.all()
    analisis_list = models.Analisis.objects.all()
    ots = models.OT.objects.all()
    elementos = models.Elementos.objects.all()

    # Pasar los datos al contexto de la plantilla
    context = {
        'odts': odts,
        'analisis_list': analisis_list,
        'ots': ots,
        'elementos': elementos,
    }
    
    return render(request, 'index.html', context)
       
    

def ODT_Module(request):
    search_query = request.GET.get('search', '')
    filter_year = request.GET.get('year', '')
    filter_month = request.GET.get('month', '')

    print(search_query)

    odts = models.ODT.objects.all()

    odts = odts.filter(
        Q(Nro_OT__icontains=search_query) |
        Q(Cliente__nombre_cliente__icontains=search_query) |  # Acceder al nombre del cliente
        Q(Proyecto__nombre__icontains=search_query) |  # Acceder al nombre del proyecto
        Q(Muestra__icontains=search_query) |
        Q(Cant_Muestra__icontains=search_query) |
        Q(Despacho__icontains=search_query) |
        Q(Envio__username__icontains=search_query) |  # Acceder al nombre de usuario del envío
        Q(Turno__icontains=search_query)
    )
    
    
    if filter_year:
        odts = odts.filter(Fec_Recep__year=filter_year)

    if filter_month:
        odts = odts.filter(Fec_Recep__month=filter_month)
    
    context = {
        'odts': odts,
        'available_years': list(models.ODT.objects.dates('Fec_Recep', 'year').values_list('Fec_Recep__year', flat=True).distinct()),
        'available_months': [
            {'value': 1, 'label': 'Enero'}, {'value': 2, 'label': 'Febrero'}, {'value': 3, 'label': 'Marzo'},
            {'value': 4, 'label': 'Abril'}, {'value': 5, 'label': 'Mayo'}, {'value': 6, 'label': 'Junio'},
            {'value': 7, 'label': 'Julio'}, {'value': 8, 'label': 'Agosto'}, {'value': 9, 'label': 'Septiembre'},
            {'value': 10, 'label': 'Octubre'}, {'value': 11, 'label': 'Noviembre'}, {'value': 12, 'label': 'Diciembre'}
        ]
    }

    return render(request, 'ODT-Site.html', context)


def ModMuestras(request):
    if request.method == 'POST':
        Contex = request.POST.get('contex')
        idODT = request.POST.get('ODTID')
        CodigoMuestra = request.POST.get('MuestraODT', '')
        Volumen = request.POST.get('valVol')
        Peso = request.POST.get('valPes')
        Disol = request.POST.get('valDis')
        muestra_id = str(request.POST.get('valID', '00'))
        targetDel = str(request.POST.get('TargetDel', ''))
        
        if len(muestra_id) == 1:
            muestra_id = "0" + muestra_id

        ID_CodeOT = CodigoMuestra + "-" + muestra_id
        print(idODT)
        try:
            odt_instance = models.ODT.objects.get(id=idODT)
        except models.ODT.DoesNotExist:
            return JsonResponse({'error': 'ODT no encontrado'}, status=404)

        try:
            if Contex == "Add":
                models.OT.objects.create(
                    id_muestra=ID_CodeOT,
                    odt=odt_instance,
                    peso_muestra=0.0,
                    volumen=0.0,
                    dilucion=0.0
                )
            elif Contex == "Mod":
                TargetOT = models.OT.objects.get(id_muestra=targetDel)
                TargetOT.dilucion = Disol
                TargetOT.volumen = Volumen
                TargetOT.peso_muestra = Peso
                TargetOT.id_muestra = ID_CodeOT
                TargetOT.save()
            elif Contex == "Del":
                TargetOT = models.OT.objects.get(id_muestra=targetDel)
                TargetOT.delete()
            else:
                return JsonResponse({'error': 'Método no permitido'}, status=405)
        except models.OT.DoesNotExist:
            return JsonResponse({'error': 'Muestra no encontrada'}, status=404)

        count_ots = models.OT.objects.filter(odt=odt_instance).count()
        odt_instance.Cant_Muestra = count_ots
        odt_instance.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def ModODT(request):
    if request.method == 'POST':
        try:
            odt_id = request.POST.get('idODT')

            odt = models.ODT.objects.get(id=odt_id)
            
            # Extraer valores del formulario
            Nro_OT = request.POST.get('Nro_OT')
            Fec_Recep = request.POST.get('Fec_Recep')
            Cliente = request.POST.get('Cliente')
            Proyecto = request.POST.get('Proyecto')
            Despacho = request.POST.get('Despacho')
            Envio = request.POST.get('Envio')
            Muestra = request.POST.get('Muestra')
            Referencia = request.POST.get('Referencia')
            Comentarios = request.POST.get('Comentarios')

            with transaction.atomic():
                # Actualizar la ODT
                odt.Nro_OT = Nro_OT
                odt.Fec_Recep = Fec_Recep
                odt.Cliente = Cliente
                odt.Proyecto = Proyecto
                odt.Despacho = Despacho
                odt.Envio = Envio
                odt.Muestra = Muestra
                odt.Referencia = Referencia
                odt.Comentarios = Comentarios
                odt.save()

                ots = models.OT.objects.filter(odt=odt)

                nuevo_id_muestras = set()
                for ot in ots:
                    id_muestra_actual = ot.id_muestra
                    parts = id_muestra_actual.rsplit('-', 1)
                    
                    if len(parts) == 2:
                        nuevo_id_muestra = f"{Muestra}-{parts[1]}"
                        if nuevo_id_muestra in nuevo_id_muestras:
                            return JsonResponse({'error': 'Ya existe un registro con el ID de muestra actualizado'}, status=400)
                        nuevo_id_muestras.add(nuevo_id_muestra)

                for ot in ots:
                    id_muestra_actual = ot.id_muestra
                    parts = id_muestra_actual.rsplit('-', 1)
                    
                    if len(parts) == 2:
                        nuevo_id_muestra = f"{Muestra}-{parts[1]}"
                        ot.id_muestra = nuevo_id_muestra
                        ot.save()

            return JsonResponse({'success': True})

        except models.ODT.DoesNotExist:
            return JsonResponse({'error': 'ODT no encontrado'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)




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

        # Obtener el análisis basado en el método de análisis de la ODT
        analisis = models.Analisis.objects.get(Analisis_metodo=odt.Analisis)

        # Obtener los elementos asociados al análisis
        elementos = analisis.Elementos.all()

        # Imprimir cada elemento asociado al análisis (opcional)
        print("Elementos asociados al análisis:")
        for elemento in elementos:
            print(f"Nombre: {elemento.nombre}, Símbolo: {elemento.simbolo}, Número Atómico: {elemento.numero_atomico}")

        # Ordenar los objetos OT por el id_muestra original
        ots_sorted = sorted(ots, key=lambda ot: ot.id_muestra)

        # Crear una nueva lista con id_muestra sin el último guion e incluir los elementos
        new_ots = []
        for ot in ots_sorted:
            cleaned_id_muestra = str(ot.id_muestra).replace("-", "")
            
            # Crear una lista de diccionarios con los detalles de cada elemento asociado al análisis
            elementos_data = [
                {
                    'nombre': elemento.nombre,
                    'simbolo': elemento.simbolo,
                    'numero_atomico': elemento.numero_atomico,
                    'masa_atomica': elemento.masa_atomica,
                }
                for elemento in elementos
            ]
            
            new_ots.append({
                'id': ot.id,
                'id_muestra': ot.id_muestra,
                'id_muestraInput': cleaned_id_muestra,
                'peso_muestra': ot.peso_muestra,
                'volumen': ot.volumen,
                'dilucion': ot.dilucion,
                'odt': ot.odt,
                'updated_at': ot.updated_at,
                'elementos': elementos_data  # Agregar la lista de elementos aquí
            })

        context = {
            "odt": odt,
            "ots": new_ots,
        }

        return render(request, 'ODT-Info.html', context)
    else:
        return HttpResponse(status=405)
    

def ODT_Info_Request(request):
    print("hola")
    if request.method == 'POST':
        odt_id = request.POST.get('odt_id')
        try:
            odt = models.ODT.objects.get(id=odt_id)
        except models.ODT.DoesNotExist:
            return JsonResponse({'error': 'ODT no encontrado'}, status=404)

        ots = models.OT.objects.filter(odt=odt)

        # Obtener el análisis basado en el método de análisis de la ODT
        try:
            analisis = models.Analisis.objects.get(Analisis_metodo=odt.Analisis)
        except models.Analisis.DoesNotExist:
            return JsonResponse({'error': 'Análisis no encontrado'}, status=404)

        # Obtener los elementos asociados al análisis
        elementos = analisis.Elementos.all()

        # Función para extraer el número de id_muestra
        def extract_number_from_id(id_muestra):
            parts = id_muestra.split('-')
            return int(parts[-1]) if parts[-1].isdigit() else 0

        # Ordenar los objetos OT
        ots_sorted = sorted(ots, key=lambda ot: extract_number_from_id(ot.id_muestra))

        # Crear una nueva lista con id_muestra sin el último guion e incluir los elementos
        new_ots = []
        for ot in ots_sorted:
            cleaned_id_muestra = str(ot.id_muestra).replace("-", "")
            
            # Crear una lista de diccionarios con los detalles de cada elemento asociado al análisis
            elementos_data = [
                {
                    'nombre': elemento.nombre,
                    'simbolo': elemento.simbolo,
                    'numero_atomico': elemento.numero_atomico,
                    'masa_atomica': elemento.masa_atomica,
                }
                for elemento in elementos
            ]

            new_ots.append({
                'id': ot.id,
                'id_muestra': ot.id_muestra,
                'id_muestraInput': cleaned_id_muestra,
                'peso_muestra': ot.peso_muestra,
                'volumen': ot.volumen,
                'dilucion': ot.dilucion,
                'odt': ot.odt.Nro_OT,
                'updated_at': ot.updated_at,
                'elementos': elementos_data  # Agregar los elementos al OT
            })

        # Datos de ODT
        odt_data = {
            'Nro_OT': odt.Nro_OT,
            'Cant_Muestra': odt.Cant_Muestra,
            'Fec_Recep': odt.Fec_Recep,
            'Cliente': {
                'id': odt.Cliente.id,
                'nombre_cliente': odt.Cliente.nombre_cliente,
            } if odt.Cliente else None,
            'Proyecto': {
                'id': odt.Proyecto.id,
                'nombre': odt.Proyecto.nombre,
            } if odt.Proyecto else None,
            'Envio': {
                'id': odt.Envio.id,
                'username': odt.Envio.username,
            } if odt.Envio else None,
            'Despacho': odt.Despacho,
            'Muestra': odt.Muestra,
            'Comentarios': odt.Comentarios,
            'Analisis': {
                'id': odt.Analisis.id,
                'Analisis_metodo': odt.Analisis.Analisis_metodo,
            }
        }

        return JsonResponse({'ots': new_ots, 'odt': odt_data})
    else:
        return HttpResponse(status=405)

def Elements_Section(request):
    elementos = models.Elementos.objects.all()
    tipos_unicos = models.Elementos.objects.values_list('tipo', flat=True).distinct()
    tipo_filtrado = request.GET.get('tipo', '')
    if tipo_filtrado:
        elementos = elementos.filter(tipo__iexact=tipo_filtrado)
    enabled_filtrado = request.GET.get('enabled', '')
    if enabled_filtrado:
        if enabled_filtrado.lower() == 'true':
            elementos = elementos.filter(enabled=True)
        elif enabled_filtrado.lower() == 'false':
            elementos = elementos.filter(enabled=False)
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



def Analysis_Section(request):
    analisis = models.Analisis.objects.all()
    tipos_unicos = models.Analisis.objects.values_list('Analisis_metodo', flat=True).distinct()
    tipo_filtrado = request.GET.get('Analisis_metodo', '')
    if tipo_filtrado:
        analisis = analisis.filter(Analisis_metodo__iexact=tipo_filtrado)
    enabled_filtrado = request.GET.get('enabled', '')
    if enabled_filtrado:
        if enabled_filtrado.lower() == 'true':
            analisis = analisis.filter(enabled=True)
        elif enabled_filtrado.lower() == 'false':
            analisis = analisis.filter(enabled=False)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        ID_Targe = request.POST.get('id', '')
    
        if action and ID_Targe:
            try:
                Target = models.Analisis.objects.get(pk=ID_Targe)
                if action == 'Activar':
                    Target.enabled = True
                elif action == 'Desactivar':
                    Target.enabled = False
                Target.save()
                return JsonResponse({'success': True})
            except models.Analisis.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Análisis no encontrado'})
    context = {
        'analisis': analisis,
        'metodos_unicos': tipos_unicos,
    }
    return render(request, "analysis.html", context)



def general_form(request, token):
    try:
        decoded_data = base64.urlsafe_b64decode(token.encode()).decode()
        data = json.loads(decoded_data)

        target_ID = data.get('id')
        context = data.get('context')
        action = data.get('action')
        stade = data.get('stade')

        print(target_ID)
        print(context)
        print(action)

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
                if request.method == "GET":
                    model.delete()
                    return redirect(reverse('elements_manager'))
        
        elif context == 'analytic':
            if action == 'add':
                form = forms.FormAnalisis()
                if request.method == 'POST':
                    form = forms.FormAnalisis(request.POST)
                    if form.is_valid():
                        form.save()
                        return redirect(reverse('analisis_manager'))
            elif action == 'mod':
                # Lógica para modificar un elemento
                model = models.Analisis.objects.get(id=target_ID)
                form = forms.FormAnalisis(instance = model)
                if request.method == 'POST':
                    form = forms.FormAnalisis(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('analisis_manager'))
                        
            elif action == 'del':
                model = models.Analisis.objects.get(id=target_ID)
                if request.method == "GET":
                    model.delete()
                    return redirect(reverse('analisis_manager'))
        elif context == 'ODT':
            if action == 'add':
                form = forms.FormODT(request.POST or None)
                if request.method == 'POST':
                    if form.is_valid():
                        try:
                            # Guardar la instancia de ODT
                            odt_instance = form.save(commit=False)
                            if odt_instance.Proyecto and odt_instance.Proyecto.cliente:
                                print(odt_instance.Proyecto.cliente)
                                odt_instance.Cliente = odt_instance.Proyecto.cliente
                            odt_instance.save()
                            ProyectDis = odt_instance.Proyecto.volVal
                            muestra_codigo = odt_instance.Muestra
                            inicio_codigo = odt_instance.InicioCodigo
                            fin_codigo = odt_instance.FinCodigo
                            
                            if inicio_codigo is not None and fin_codigo is not None:
                                if fin_codigo < inicio_codigo:
                                    form.add_error(None, 'El número final del código debe ser mayor o igual al número inicial.')
                                else:
                                    for codigo in range(inicio_codigo, fin_codigo + 1):
                                        codigo_completo = f"{muestra_codigo}-{codigo:02d}"
                                        
                                        # Verificar si el código ya existe antes de crear el registro
                                        if models.OT.objects.filter(id_muestra=codigo_completo).exists():
                                            form.add_error(None, f'El código de muestra {codigo_completo} ya existe en OT.')
                                            break  # Salir del bucle si encontramos un duplicado
                                        
                                        # Crear el registro en OT
                                        models.OT.objects.create(
                                            id_muestra=codigo_completo,
                                            odt=odt_instance,
                                            peso_muestra=0.0,
                                            volumen=ProyectDis,
                                            dilucion=0.0
                                        )
                                    
                                    if not form.errors:
                                        return redirect(reverse('Main_ODT'))
                            else:
                                form.add_error(None, 'Debe especificar el rango de códigos de muestra.')
                        except IntegrityError as e:
                            # Manejar errores de unicidad
                            if 'duplicate key value violates unique constraint' in str(e):
                                form.add_error(None, 'Uno o más códigos de muestra ya existen. Por favor, revise los códigos e intente de nuevo.')
                            else:
                                form.add_error(None, 'Error al guardar el registro. Por favor, intente de nuevo.')
                            print(e)  # Para depuración
                    else:
                        messages.add_message(request=request, level=messages.ERROR, message='El usuario no tiene permiso para acceder aquí')
                        print(form.errors)
            elif action == 'mod':
                print("Modificar ODTs")
                model = models.ODT.objects.get(id=target_ID)
                form = forms.FormODT(instance = model)
                if request.method == 'POST':
                    form = forms.FormODT(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('Main_ODT'))
                    
            elif action == 'del':
                print("EIMINAR ODT")
                model = models.ODT.objects.get(id=target_ID)
                models.OT.objects.filter(odt=model).delete()
                model.delete()
                print("Deleted")
                return redirect(reverse('Main_ODT'))
        
        elif context == 'Read':
            # Lógica para 'Read'
            result_message = f'Lectura {target_ID} procesada con éxito.'


       
        data = {'form':form, 'id':target_ID, "contexModel": context, "action": action}
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


def get_proyectos(request):
    cliente_id = request.GET.get('cliente_id')
    proyectos = models.Proyecto.objects.filter(cliente_id=cliente_id)
    data = {
        'proyectos': list(proyectos.values('id', 'nombre'))
    }
    return JsonResponse(data)