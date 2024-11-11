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
from django.db.models import Q, Min
from decimal import Decimal


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

    print(search_query)

    odts = models.ODT.objects.all()

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

@login_required(login_url='/login')
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
            Prefijo = request.POST.get('Prefijo')
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
                odt.Prefijo = Prefijo
                odt.Referencia = Referencia
                odt.Comentarios = Comentarios
                odt.save()

                ots = models.OT.objects.filter(odt=odt)

                nuevo_id_muestras = set()
                for ot in ots:
                    id_muestra_actual = ot.id_muestra
                    parts = id_muestra_actual.rsplit('-', 1)
                    
                    if len(parts) == 2:
                        nuevo_id_muestra = f"{Prefijo}-{parts[1]}"
                        if nuevo_id_muestra in nuevo_id_muestras:
                            return JsonResponse({'error': 'Ya existe un registro con el ID de muestra actualizado'}, status=400)
                        nuevo_id_muestras.add(nuevo_id_muestra)

                for ot in ots:
                    id_muestra_actual = ot.id_muestra
                    parts = id_muestra_actual.rsplit('-', 1)
                    
                    if len(parts) == 2:
                        nuevo_id_muestra = f"{Prefijo}-{parts[1]}"
                        ot.id_muestra = nuevo_id_muestra
                        ot.save()

            return JsonResponse({'success': True})

        except models.ODT.DoesNotExist:
            return JsonResponse({'error': 'ODT no encontrado'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required(login_url='/login')
def HT_Module(request):
    search_query = request.GET.get('search', '')
    estado_filter = request.GET.get('estado', '')  # Obtenemos el filtro del estado

    hts = (models.HojaTrabajo.objects
           .values('ID_HDT')
           .annotate(min_id=Min('id'))
           .values('min_id'))
    
    hts = models.HojaTrabajo.objects.filter(id__in=[ht['min_id'] for ht in hts])

    # Filtro por estado (Pendiente, Cerrado, o Todas)
    if estado_filter == 'Pendiente':
        hts = hts.filter(confirmar_balanza=False)  # Filtrar por Pendiente (False)
    elif estado_filter == 'Cerrado':
        hts = hts.filter(confirmar_balanza=True)  # Filtrar por Cerrado (True)

    # Filtro de búsqueda por palabra clave
    if search_query:
        hts = hts.filter(
            Q(ID_HDT__icontains=search_query) |
            Q(odt__id__icontains=search_query) |
            Q(MuestraMasificada__Prefijo__icontains=search_query) |
            Q(MetodoAnalisis__nombre__icontains=search_query)
        )

    context = {
        'hts': hts,
    }

    return render(request, 'Hoja_Trabajo.html', context)



def Request_HT(request):
    if request.method == 'GET':
        id_hdt = request.GET.get('id')
        muestras = models.HojaTrabajo.objects.filter(ID_HDT=id_hdt)
        data = []
        
        for muestra in muestras:
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
                'ID_HDT': muestra.ID_HDT,
                'estado': 'Cerrado' if muestra.confirmar_balanza else 'Pendiente',
                'estandar': ', '.join(estandar.Nombre for estandar in muestra.Estandar.all()),
                'metodo_analisis': muestra.MetodoAnalisis.nombre,
                'muestra_masificada': muestra.MuestraMasificada.Prefijo,
                'tipo': muestra.Tipo,
                'duplicado': muestra.Duplicado,
                'elementos': elementos_data,
                'peso_elemento': peso_elemento_text
            })
        
        return JsonResponse({'muestras': data})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)



@login_required(login_url='/login')
def Balanza_Module(request):
    if request.method == 'POST':
        id_hdt = request.POST.get('id')
        print(f'ID recibido en Balanza: {id_hdt}')

        # Obtener todas las hojas de trabajo que tengan el mismo ID_HDT
        hojas_trabajo = models.HojaTrabajo.objects.filter(ID_HDT=id_hdt)

        if not hojas_trabajo.exists():
            return HttpResponse("No se encontró ninguna Hoja de Trabajo con el ID especificado.", status=404)

        # Obtener la primera muestra asociada a las hojas de trabajo filtradas
        primera_muestra = models.Muestra.objects.filter(hoja_trabajo__in=hojas_trabajo, indexCurv=1).first()

        if primera_muestra is None:
            return HttpResponse("No se encontraron muestras para la Hoja de Trabajo especificada.", status=404)

        # Filtrar las muestras con el mismo tipo de 'elemento' que la primera muestra
        tipo_elemento = primera_muestra.elemento
        muestras_balanza = models.Muestra.objects.filter(
            hoja_trabajo__in=hojas_trabajo,
            elemento=tipo_elemento,
            indexCurv=1
        )

        context = {'muestras_balanza': muestras_balanza}
        return render(request, 'Balanza.html', context)

    return render(request, 'Balanza.html')
    

def Save_M(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Los datos se envían en formato JSON
            muestras = data.get('muestras', [])
            
            # Iterar sobre las muestras recibidas
            for muestra_data in muestras:
                prefijo = muestra_data.get('prefijo')
                peso_m = muestra_data.get('peso_m')

                # Filtrar la muestra por Prefijo (muestraMasificada.Prefijo)
                muestra = models.Muestra.objects.filter(muestraMasificada__Prefijo=prefijo).first()
                
                if muestra:
                    # Reemplazar el punto (.) por una coma (,) en el peso
                    peso_m = Decimal(str(peso_m).replace(',', '.'))
                    
                    # Actualizar el valor de peso_m
                    muestra.peso_m = peso_m
                    muestra.save()

                    print(f"Actualizado - Prefijo: {prefijo}, Peso: {peso_m}")

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

def Confirm_M(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            muestras = data.get('muestras', [])
            
            for muestra_data in muestras:
                prefijo = muestra_data.get('prefijo')
                peso_m = muestra_data.get('peso_m')

                muestra = models.Muestra.objects.filter(muestraMasificada__Prefijo=prefijo).first()
                
                if muestra:

                    peso_m = Decimal(str(peso_m).replace(',', '.'))
                    
                    muestra.peso_m = peso_m
                    muestra.save()

                    hoja_trabajo = muestra.hoja_trabajo
                    if hoja_trabajo:
                        hoja_trabajo.confirmar_balanza = True
                        hoja_trabajo.save()

                    print(f"Confirmada - Prefijo: {prefijo}, Confirmar Balanza: {hoja_trabajo.confirmar_balanza}")

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
        

@login_required(login_url='/login')
def PI_Module(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_hdt = data.get('id')
        print(f'ID recibido en Absorción: {id_hdt}')
        
        return JsonResponse({'success': True})
    
    return render(request, 'Puesto-Absorcion.html')




@login_required(login_url='/login')
def PT_Module(request):


    return render(request, 'Puesto-Trabajo.html')


@login_required(login_url='/login')
def ODT_Info(request):
    if request.method == 'POST':
        odt_id = request.POST.get('odt_id')
        odt = models.ODT.objects.get(id=odt_id)
        muestras_M = models.MuestraMasificada.objects.filter(odt=odt)

     
        context = {"odt": odt, "Muestras": muestras_M}

        return render(request, 'ODT-Info.html', context)
    else:
        return HttpResponse(status=405)
    
@login_required(login_url='/login')
def ODT_Info_Request(request):
    if request.method == 'POST':
        odt_id = request.POST.get('odt_id')
        try:
            odt = models.ODT.objects.get(id=odt_id)
        except models.ODT.DoesNotExist:
            return JsonResponse({'error': 'ODT no encontrado'}, status=404)
        
        ots = models.OT.objects.filter(odt=odt)

        try:
            analisis = models.Analisis.objects.get(Analisis_metodo=odt.Analisis)
        except models.Analisis.DoesNotExist:
            return JsonResponse({'error': 'Análisis no encontrado'}, status=404)

        elementos = analisis.Elementos.all()

        def extract_number_from_id(id_muestra):
            parts = id_muestra.split('-')
            return int(parts[-1]) if parts[-1].isdigit() else 0
        
        ots_sorted = sorted(ots, key=lambda ot: extract_number_from_id(ot.id_muestra))
        new_ots = []
        for ot in ots_sorted:
            cleaned_id_muestra = str(ot.id_muestra).replace("-", "")
            
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
                'elementos': elementos_data 
            })

        odt_data = {
            'Nro_OT': odt.Nro_OT,
            'Cant_Muestra': odt.Cant_Muestra,
            'Fec_Recep': odt.Fec_Recep,
            'Cliente': {
                'id': odt.Cliente.id,
                'nombre': odt.Cliente.nombre,
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
            'Prefijo': odt.Prefijo,
            'Comentarios': odt.Comentarios,
            'Analisis': {
                'id': odt.Analisis.id,
                'Analisis_metodo': odt.Analisis.Analisis_metodo,
            }
        }

        return JsonResponse({'ots': new_ots, 'odt': odt_data})
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
        if context not in ['element', 'analytic', 'ODT', 'Read', 'curv']:
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
                        form.save()
                        return redirect(reverse('Main_ODT'))
            elif action == 'mod':
                model = models.ODT.objects.get(id=target_ID)
                form = forms.ODTForm(instance = model)
                model.Fec_Recep = model.Fec_Recep.strftime('%Y-%m-%d')
                model.Fec_Finalizacion = model.Fec_Finalizacion.strftime('%Y-%m-%d')
                form = forms.ODTForm(instance = model)
                if request.method == 'POST':
                    form = forms.ODTForm(request.POST, instance=model)
                    if form.is_valid():
                        form = form.save()
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

    user_data = {
        'email': user.username,         
        'full_name': f"{user.first_name} {user.last_name}",
        'role': user.rolname,
        'URLReact':settings.URL_REACT,
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