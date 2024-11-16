import base64
import json
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect
from api import models, forms
from django.urls import reverse
from django.db import IntegrityError, transaction, connection
from django.db.models import Q, Min, F
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
import threading
import serial
import serial.tools.list_ports
from serial.tools import list_ports


@login_required(login_url='/login')
def requestAcces(request):
    return redirect("/index")


def Sitio_Web(request):
    return render(request, "Inicio.html")



def login_view(request):

    if not settings.ENABLED_LOGIN_LOCAL:
        return HttpResponseRedirect(settings.URL_REACT)

    if request.user.is_authenticated:
        return redirect('/index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if request.user.is_authenticated:
                return redirect('/index')
            else:
                return render(request, "login.html", {'form': form, 'error': "Error de autenticación."})
    else:
        form = AuthenticationForm()
    
    return render(request, "login.html", {'form': form})



def logout_View(request):
    try:
        # Cerrar sesión del usuario
        logout(request)
        print("Usuario deslogueado correctamente")

        # Opcional: Limpiar el token si estás manejando la autenticación basada en tokens
        if hasattr(request.user, 'token'):
            request.user.token = None
            request.user.save()
            print("Token eliminado del usuario")
        if settings.ENABLED_LOGIN_LOCAL == False: 
            return HttpResponseRedirect(settings.URL_REACT)
        else:
            return redirect(reverse('login_View'))

    except Exception as e:
        print(f"Error al desloguear usuario: {e}")
        message = f"Error al desloguear usuario: {str(e)}"
        return JsonResponse({'tipo': 'error', 'message': message}, status=500)
    


@login_required(login_url='/login')
def Main(request):
    return render(request, 'index.html')
       
    
@login_required(login_url='/login')
def ODT_Module(request):
    search_query = request.GET.get('search', '')
    filter_year = request.GET.get('year', '')
    filter_month = request.GET.get('month', '')

    odts = models.ODT.objects.all()

    # Si el prefijo "WSS" está en la búsqueda, eliminarlo para buscar por el ID
    if search_query.startswith("WSS"):
        search_query = search_query[3:]

    odts = odts.filter(
        Q(id__icontains=search_query) |
        Q(Proyecto__nombre__icontains=search_query) |
        Q(Prefijo__icontains=search_query) |
        Q(Cant_Muestra__icontains=search_query) |
        Q(Prioridad__icontains=search_query) |
        Q(TipoMuestra__icontains=search_query) | 
        Q(Referencia__icontains=search_query) |
        Q(Cliente__nombre__icontains=search_query) |
        Q(Proyecto__nombre__icontains=search_query) |
        Q(Responsable__icontains=search_query)
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



@login_required(login_url='/login')
def HT_Module(request):
    search_query = request.GET.get('search', '')
    estado_filter = request.GET.get('estado', '') 

    hts = (models.HojaTrabajoQuimico.objects
           .values('ID_HDT')
           .annotate(min_id=Min('HojaTrabajo__id'))
           .values('min_id'))
    
    hts = models.HojaTrabajo.objects.filter(id__in=[ht['min_id'] for ht in hts]).annotate(
        ID_HDT=F('hojas_trabajo_target__ID_HDT'),
        confirmar_balanza=F('hojas_trabajo_target__confirmar_balanza')
    )

    if estado_filter == 'Pendiente':
        hts = hts.filter(confirmar_balanza=False)
    elif estado_filter == 'Cerrado':
        hts = hts.filter(confirmar_balanza=True)

    if search_query:
        hts = hts.filter(
            Q(hojas_trabajo_target__ID_HDT__icontains=search_query) |
            Q(odt__id__icontains=search_query) |
            Q(MuestraMasificada__Prefijo__icontains=search_query) |
            Q(MetodoAnalisis__nombre__icontains=search_query)
        )
    data = []
    for ht in hts:
        data.append({
            'id': ht.id,
            'ID_HDT': ht.ID_HDT,
            'estado': 'Cerrado' if ht.confirmar_balanza else 'Pendiente',
            'odt': ht.odt.id,
            'estandar': [estandar.Nombre for estandar in ht.Estandar.all()],
            'metodo_analisis': ht.MetodoAnalisis.nombre,
            'muestra_masificada': ht.MuestraMasificada.Prefijo,
            'tipo': ht.Tipo,
            'duplicado': ht.Duplicado,
        })

    data_json = json.dumps(data)

    context = {
        'hts': hts,
        'hts_json': data_json 
    }

    return render(request, 'Hoja_Trabajo.html', context)


def Request_HT(request):
    if request.method == 'GET':
        id_hdt = request.GET.get('id')

        hojas_trabajo_quimico = models.HojaTrabajoQuimico.objects.filter(ID_HDT=id_hdt).order_by('ID_HDT')

        data = []
        
        for hoja_quimico in hojas_trabajo_quimico:
            muestra = hoja_quimico.HojaTrabajo 
            elementos_data = [
                {
                    'nombre': elemento.nombre,
                    'gramos': elemento.gramos,
                    'miligramos': elemento.miligramos
                }
                for elemento in muestra.MetodoAnalisis.elementos.all()
            ]
            muestras_filtradas = models.Muestra.objects.filter(hoja_trabajo=muestra, indexCurv=1)

            pesos_elementos = {}
            for m in muestras_filtradas:
                elemento_nombre = m.elemento
                if elemento_nombre in pesos_elementos:
                    pesos_elementos[elemento_nombre] += m.peso_m
                else:
                    pesos_elementos[elemento_nombre] = m.peso_m

            peso_elemento_text = ', '.join(f"Peso de {elemento}: {peso}g" for elemento, peso in pesos_elementos.items())
            
            data.append({
                'id': muestra.id,
                'ID_HDT': hoja_quimico.ID_HDT,
                'estado': 'Cerrado' if hoja_quimico.confirmar_balanza else 'Pendiente',
                'estandar': ', '.join(estandar.Nombre for estandar in muestra.Estandar.all()),
                'metodo_analisis': muestra.MetodoAnalisis.nombre,
                'muestra_masificada': muestra.MuestraMasificada.Prefijo,
                'tipo': muestra.Tipo,
                'duplicado': muestra.Duplicado,
                'elementos': elementos_data,
                'peso_elemento': peso_elemento_text
            })
        
        data = sorted(data, key=lambda x: x['id'])

        return JsonResponse({'muestras': data})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)




@login_required(login_url='/login')
def Balanza_Module(request):
    if request.method == 'POST':
        id_hdt = request.POST.get('id')
        print(f'ID recibido en Balanza: {id_hdt}')

        hojas_trabajo_quimico = models.HojaTrabajoQuimico.objects.filter(ID_HDT=id_hdt)

        targetHDT_Quimico = hojas_trabajo_quimico.first()

        if not hojas_trabajo_quimico.exists():
            return render(request, 'Balanza.html')

        hojas_trabajo = models.HojaTrabajo.objects.filter(id__in=[htq.HojaTrabajo.id for htq in hojas_trabajo_quimico])

        primera_muestra = models.Muestra.objects.filter(hoja_trabajo__in=hojas_trabajo, indexCurv=1).first()

        if primera_muestra is None:
            return render(request, 'Balanza.html')

        tipo_elemento = primera_muestra.elemento
        muestras_balanza = models.Muestra.objects.filter(
            hoja_trabajo__in=hojas_trabajo,
            elemento=tipo_elemento,
            indexCurv=1
        ).order_by('muestraMasificada__Prefijo')
        context = {'muestras_balanza': muestras_balanza, 'id_hdt': id_hdt, 'stade': targetHDT_Quimico.confirmar_balanza}
        return render(request, 'Balanza.html', context)

    return render(request, 'Balanza.html')
    

def Save_M(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            muestras = data.get('muestras', [])
            ID_HDT = data.get('id')
            print(f"ID_HDT recibido: {ID_HDT}")

            for muestra_data in muestras:
                prefijo = muestra_data.get('prefijo')
                peso_m = muestra_data.get('peso_m')

                # Convertir peso a Decimal
                peso_m = Decimal(str(peso_m).replace(',', '.'))

                # Filtrar muestras específicas usando el ID_HDT y el Prefijo
                muestras = models.Muestra.objects.filter(
                    muestraMasificada__Prefijo=prefijo,
                    hoja_trabajo__hojas_trabajo_target__ID_HDT=ID_HDT  # Filtrar por HojaTrabajo y ID_HDT
                )

                # Actualizar el campo peso_m en las muestras filtradas
                for muestra in muestras:
                    muestra.peso_m = peso_m
                    muestra.save()
                    print(f"Actualizado - Prefijo: {prefijo}, Elemento: {muestra.elemento}, Peso: {peso_m}")
            models.Novedades.objects.create(
                tipo_model = 'Hoja de trabajo',
                accion="Modificar",
                modelt_id=str(ID_HDT),
                fecha=timezone.now(),
                usuario = request.user
            )
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos'}, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

def Confirm_M(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            muestras = data.get('muestras', [])
            ID_HDT = data.get('id')
            print(f"ID_HDT recibido: {ID_HDT}")

            for muestra_data in muestras:
                prefijo = muestra_data.get('prefijo')
                peso_m = muestra_data.get('peso_m')

                muestras = models.Muestra.objects.filter(
                    muestraMasificada__Prefijo=prefijo,
                    hoja_trabajo__hojas_trabajo_target__ID_HDT=ID_HDT
                )

                peso_m = Decimal(str(peso_m).replace(',', '.'))
                
                for muestra in muestras:
                    muestra.peso_m = peso_m
                    muestra.save()

                    hoja_trabajo_quimico = models.HojaTrabajoQuimico.objects.filter(
                        HojaTrabajo=muestra.hoja_trabajo,
                        ID_HDT=ID_HDT
                    ).first()

                    if hoja_trabajo_quimico:
                        hoja_trabajo_quimico.confirmar_balanza = True
                        hoja_trabajo_quimico.save()

                    print(f"Confirmada - Prefijo: {prefijo}, Confirmar Balanza: {hoja_trabajo_quimico.confirmar_balanza}")
            
            models.Novedades.objects.create(
                tipo_model = 'Hoja de trabajo',
                accion="Balanza",
                modelt_id=str(ID_HDT),
                fecha=timezone.now(),
                usuario = request.user
            )
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos'}, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
        



@login_required(login_url='/login')
def PI_Module(request):
    if request.method == 'POST':
        id_hdt = request.POST.get('id')
        print(f'ID recibido en Absorción: {id_hdt}')

        hojas_trabajo_quimico = models.HojaTrabajoQuimico.objects.filter(ID_HDT=id_hdt).order_by('ID_HDT')
        targetHDT_Quimico = hojas_trabajo_quimico.first()

        if not hojas_trabajo_quimico.exists():
            return render(request, 'Puesto-Absorcion.html')

        hojas_trabajo = models.HojaTrabajo.objects.filter(
            id__in=[htq.HojaTrabajo.id for htq in hojas_trabajo_quimico]
        ).order_by('id')

        odt_ids = hojas_trabajo.values_list('odt_id', flat=True)

        muestras_M = models.MuestraMasificada.objects.filter(odt_id__in=odt_ids)

        muestras = models.Muestra.objects.filter(
            hoja_trabajo__in=hojas_trabajo
        ).order_by('hoja_trabajo__hojas_trabajo_target__ID_HDT', 'hoja_trabajo__id', 'elemento', 'indexCurv')

        muestras_count = muestras_M.count()

        resultados = models.Resultado.objects.filter(
            hoja_trabajo__in=hojas_trabajo
        ).order_by('hoja_trabajo__hojas_trabajo_target__ID_HDT', 'hoja_trabajo__id', 'muestra__elemento', 'fecha_emision')

        context = {
            'id_hdt': id_hdt,
            'hojas_trabajo': hojas_trabajo,
            'muestras': muestras,
            'muestras_M': muestras_M,
            'resultados': resultados,
            'muestras_count': muestras_count
        }
        
        return render(request, 'Puesto-Absorcion.html', context)

    return render(request, 'Puesto-Absorcion.html')



@login_required(login_url='/login')
def PT_Module(request):
    fecha_actual = timezone.now()

    acciones_registros = models.Novedades.objects.filter(
        accion__in=['Crear', 'Modificar', 'Eliminar']
    ).order_by('-fecha') 

    procesos_hojas_trabajo = models.Novedades.objects.filter(
        accion__in=['Balanza', 'Absorcion']
    ).order_by('-fecha')

    context = {
        'acciones_registros': acciones_registros,
        'procesos_hojas_trabajo': procesos_hojas_trabajo,
    }

    return render(request, 'Puesto-Trabajo.html', context)


@login_required(login_url='/login')
def ODT_Info(request):
    if request.method == 'POST':
        odt_id = request.POST.get('odt_id')
        odt = models.ODT.objects.get(id=odt_id)
        muestras_M = models.MuestraMasificada.objects.filter(odt=odt)

        HDT = models.HojaTrabajo.objects.filter(odt=odt)
        HDT_Quimico = models.HojaTrabajoQuimico.objects.filter(HojaTrabajo__in=HDT).values('ID_HDT').distinct()

        # Agregar HDT_Quimico al contexto
        context = {"odt": odt, "Muestras": muestras_M, "HDT_Quimico": HDT_Quimico}

        return render(request, 'ODT-Info.html', context)
    else:
        return HttpResponse(status=405)
    
@login_required(login_url='/login')
def Elements_Section(request):
    elementos = models.Elementos.objects.all()

    tipo_filtrado = request.GET.get('tipo', '')
    if tipo_filtrado:
        elementos = elementos.filter(nombre__icontains=tipo_filtrado)

    for elemento in elementos:
        elemento.curvaturas = models.CurvaturaElementos.objects.filter(elemento=elemento)

    context = {
        'elementos': elementos,
    }

    return render(request, "Elements.html", context)

@login_required(login_url='/login')
def Analysis_Section(request):
    analisis = models.MetodoAnalisis.objects.all()
    query = request.GET.get('search', '') 
    if query:
        analisis = analisis.filter(nombre__icontains=query)  

    context = {
        'analisis': analisis,
        'query': query, 
    }
    return render(request, "analysis.html", context)


@login_required(login_url='/login')
def general_form(request, token):
    try:
        decoded_data = base64.urlsafe_b64decode(token.encode()).decode()
        data = json.loads(decoded_data)

        target_ID = str(data.get('id'))
        context = data.get('context')
        action = data.get('action')
        stade = data.get('stade')

        form = None
        model = None

        # Verificar el estado
        if stade != "acces":
            return HttpResponseForbidden("Acceso no autorizado.")
        # Validar contexto y acción
        if context not in ['element', 'analytic', 'ODT', 'Read', 'curv', 'HDT']:
            return HttpResponseForbidden("Contexto no válido.")
        if action not in ['add', 'mod', 'del']:
            return HttpResponseForbidden("Acción no válida.")
        # Procesar según el contexto y la acción
        if context == 'element':
            if action == 'add':
                form = forms.ElementosForm()
                if request.method == 'POST':
                    form = forms.ElementosForm(request.POST)
                    if form.is_valid():
                        form.save()
                        return redirect(reverse('elements_manager'))
            elif action == 'mod':
                # Lógica para modificar un elemento
                model = models.Elementos.objects.get(id=target_ID)
                form = forms.ElementosForm(instance = model)
                if request.method == 'POST':
                    form = forms.ElementosForm(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('elements_manager'))
            elif action == 'del':
                model = models.Elementos.objects.get(id=target_ID)
                if request.method == "GET":
                    model.delete()
                    messages.add_message(request=request, level=messages.SUCCESS, message='Elemento eliminado con exito')
                    return redirect(reverse('elements_manager'))
                
        if context == 'ODT':
            if action == 'add':
                form = forms.ODTForm()
                if request.method == 'POST':
                    form = forms.ODTForm(request.POST)
                    if form.is_valid():
                        odt_instance = form.save()
                        models.Novedades.objects.create(
                            tipo_model='Orden de trabajo',
                            accion="Crear",
                            modelt_id=str(odt_instance.Prefijo),
                            fecha=timezone.now(),
                            usuario = request.user
                        )
                        return redirect(reverse('Main_ODT'))
            elif action == 'mod':
                model = models.ODT.objects.get(id=target_ID)
                form = forms.ODTForm(instance=model)
                model.Fec_Recep = model.Fec_Recep.strftime('%Y-%m-%d')
                model.Fec_Finalizacion = model.Fec_Finalizacion.strftime('%Y-%m-%d')
                form = forms.ODTForm(instance=model)

                if request.method == 'POST':
                    form = forms.ODTForm(request.POST, instance=model)
                    if form.is_valid():
                        try:
                            odt_instance = form.save()
                            models.Novedades.objects.create(
                                tipo_model='Orden de trabajo',
                                accion="Modificar",
                                modelt_id=str(odt_instance.Prefijo),
                                fecha=timezone.now(),
                                usuario=request.user
                            )
                            messages.add_message(request=request, level=messages.SUCCESS, message='Se ajustó la orden de trabajo con éxito.')
                            return redirect(reverse('Main_ODT'))
                        except ValidationError as e:
                            messages.add_message(request=request, level=messages.ERROR, message='La orden de trabajo ya tiene una hoja de trabajo asociada.')
                            return redirect(reverse('Main_ODT'))
                    else:
                        # Si el formulario no es válido
                        messages.add_message(request=request, level=messages.ERROR, message='Error al ajustar la orden de trabajo. Por favor, verifica los datos ingresados.')
                        return redirect(reverse('Main_ODT'))
            elif action == 'del':
                model = models.ODT.objects.get(id=target_ID)
                if request.method == "GET":
                    Muestra_M = models.MuestraMasificada.objects.filter(odt=model)
                    Muestras_HDT = models.Muestra.objects.filter(muestraMasificada__in=Muestra_M)   
                    if Muestras_HDT.exists():
                        messages.add_message(request=request, level=messages.ERROR, message='Algunas muestras estan operativas en una hoja de trabajo, eliminalas antes de aplicar esta acción')
                        return redirect(reverse('Main_ODT'))
                    else:
                        models.Novedades.objects.create(
                            tipo_model='Orden de trabajo',
                            accion="Eliminar",
                            modelt_id=str(model.Prefijo),
                            fecha=timezone.now(),
                            usuario = request.user
                        )
                        model.delete()
                        messages.add_message(request=request, level=messages.SUCCESS, message='Se eliminó la orden de trabajo con exito')
                        return redirect(reverse('Main_ODT'))

        if context == 'curv':
            if action == 'add':
                form = forms.CurvaturaForm()
                if request.method == 'POST':
                    form = forms.CurvaturaForm(request.POST)
                    if form.is_valid():
                        form.save()
                        return redirect(reverse('elements_manager'))
            elif action == 'mod':
                # Lógica para modificar un elemento
                model = models.CurvaturaElementos.objects.get(id=target_ID)
                form = forms.CurvaturaForm(instance = model)
                if request.method == 'POST':
                    form = forms.CurvaturaForm(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('elements_manager'))
                        
            elif action == 'del':
                model = models.CurvaturaElementos.objects.get(id=target_ID)
                if request.method == "GET":
                    model.delete()
                    return redirect(reverse('elements_manager'))
        
        elif context == 'analytic':
            if action == 'add':
                form = forms.MetodoAnalisisForm()
                if request.method == 'POST':
                    form = forms.MetodoAnalisisForm(request.POST)
                    if form.is_valid():
                        form.save()
                        return redirect(reverse('analisis_manager'))
            elif action == 'mod':
                # Lógica para modificar un elemento
                model = models.MetodoAnalisis.objects.get(id=target_ID)
                form = forms.MetodoAnalisisForm(instance = model)
                if request.method == 'POST':
                    form = forms.MetodoAnalisisForm(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
                        return redirect(reverse('analisis_manager'))
                        
            elif action == 'del':
                model = models.MetodoAnalisis.objects.get(id=target_ID)
                if request.method == "GET":
                    model.delete()
                    return redirect(reverse('analisis_manager'))

        if context == 'HDT':
            if action == 'add':
                form = forms.HojaTrabajoGeneralForm()
                if request.method == 'POST':
                    form = forms.HojaTrabajoGeneralForm(request.POST)
                    if form.is_valid():
                        hdt_instance = form.save()

                        hoja_trabajo_quimico = hdt_instance.hojas_trabajo_target.first()

                        if hoja_trabajo_quimico:
                            models.Novedades.objects.create(
                                tipo_model='Hoja de trabajo',
                                accion="Crear",
                                modelt_id=hoja_trabajo_quimico.ID_HDT,  
                                fecha=timezone.now(),
                                usuario=request.user
                            )
                        return redirect(reverse('Main_ODT'))
            
            elif action == 'mod':
                hoja_trabajo_quimico = models.HojaTrabajoQuimico.objects.filter(ID_HDT=target_ID).first()
                
                if not hoja_trabajo_quimico:
                    messages.add_message(request=request, level=messages.ERROR, message='No se encontró la hoja de trabajo química.')
                    return redirect(reverse('Main_ODT'))

                hoja_trabajo = hoja_trabajo_quimico.HojaTrabajo

                form = forms.HojaTrabajoGeneralForm(instance=hoja_trabajo)
                if request.method == 'POST':
                    form = forms.HojaTrabajoGeneralForm(request.POST, instance=hoja_trabajo)
                    if form.is_valid():
                        hoja_trabajo_instance = form.save()
                        models.Novedades.objects.create(
                            tipo_model='Hoja de trabajo',
                            accion="Modificar",
                            modelt_id=hoja_trabajo_quimico.ID_HDT,  
                            fecha=timezone.now(),
                            usuario=request.user
                        )
                        messages.add_message(request=request, level=messages.SUCCESS, message='Hoja de trabajo modificada con éxito.')
                        return redirect(reverse('Main_ODT'))
                    else:
                        messages.add_message(request=request, level=messages.ERROR, message='Error al modificar la hoja de trabajo. Verifica los datos ingresados.')
                        return redirect(reverse('Main_ODT'))
    
            elif action == 'del':
                try:
                    models_hoja_trabajo_quimico = models.HojaTrabajoQuimico.objects.filter(ID_HDT=target_ID)
                    if not models_hoja_trabajo_quimico.exists():
                        messages.add_message(request=request, level=messages.ERROR, message='No se encontró el registro a eliminar')
                        return redirect(reverse('Main_ODT'))
                    hoja_trabajos = []
                    for model in models_hoja_trabajo_quimico:
                        hoja_trabajos.append(model.HojaTrabajo)
                    models_hoja_trabajo_quimico.delete()
                    for hoja_trabajo in set(hoja_trabajos):
                        hoja_trabajo.delete()
                    models.Novedades.objects.create(
                            tipo_model='Hoja de trabajo',
                            accion="Eliminar",
                            modelt_id=hoja_trabajo_quimico.ID_HDT,  
                            fecha=timezone.now(),
                            usuario=request.user
                        )
                    messages.add_message(request=request, level=messages.SUCCESS, message='Hojas de trabajo eliminadas con éxito')
                    return redirect(reverse('Main_ODT'))

                except Exception as e:
                    messages.add_message(request=request, level=messages.ERROR, message=f'Error al eliminar las hojas de trabajo: {str(e)}')
                    return redirect(reverse('Main_ODT'))


        
        elif context == 'Read':
            # Lógica para 'Read'
            result_message = f'Lectura {target_ID} procesada con éxito.'


       
        data = {'form':form, 'id':target_ID, "contexModel": context, "action": action}
        return render(request, "General_form.html", data)

    except Exception as e:
        # En caso de error, retornar una respuesta de error
        return HttpResponseForbidden(f"Error al procesar el token: {str(e)}")
    



@login_required(login_url='/login')
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


def check_db_connection(request):
    try:
        connection.ensure_connection()
        return JsonResponse({'status': 'success', 'message': 'Database is connected'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Failed to connect to the database: {str(e)}'})
    
def get_user_data(request):
    user = request.user

    URL_React = ""

    if settings.ENABLED_LOGIN_LOCAL:
       URL_React = settings.URL_LOCAL
    else:
        URL_React = settings.URL_REACT
    user_data = {
        'email': user.username,         
        'full_name': f"{user.first_name} {user.last_name}",
        'role': user.rolname,
        'URLReact':URL_React,
        'LocalURL':settings.URL_LOCAL          
    }
    return JsonResponse(user_data)



def servicios(request):
    return render(request, 'servicios.html')


def sobre_nosostros(request):
    return render(request, 'sobre_nosotros.html')


def recursos(request):
    return render(request, 'recursos.html')


def noticias(request):
    return render(request, 'noticias.html')


def contacto(request):
    return render(request, 'contacto.html')




def listen_to_balance(port):
    event_list = []
    try:
        # Configura la conexión serial con el puerto especificado
        ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        for _ in range(10):  # Leer solo un número limitado de eventos para la prueba
            line = ser.readline().decode('utf-8').strip()
            if line:
                event_list.append(line)
    except Exception as e:
        event_list.append(f"Error: {str(e)}")
    return event_list

# View to render the tester page
def tester_balanza(request):
    return render(request, 'tester_balanza.html')

# API view to fetch events dynamically
def get_events(request):
    port = request.GET.get('port')
    if not port:
        return JsonResponse({'status': 'error', 'message': 'No se proporcionó un puerto.'})

    # Verificar si el puerto es válido
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    if port not in available_ports:
        return JsonResponse({'status': 'error', 'message': f'El puerto {port} no es válido. Puertos disponibles: {", ".join(available_ports)}'})

    # Intentar leer datos del puerto
    try:
        ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        events = []
        for _ in range(5):  # Leer hasta 5 líneas como prueba
            line = ser.readline().decode('utf-8').strip()
            if line:
                events.append(line)
        ser.close()
        return JsonResponse({'status': 'success', 'events': events})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
def list_usb_ports(request):
    ports = [p.device for p in list_ports.comports()]
    return JsonResponse({'status': 'success', 'ports': ports})