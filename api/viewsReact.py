from asyncio.log import logger
from django.conf import settings
from django.core import signing
from datetime import datetime, timedelta
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import AnalisisCuS4FeS4MoS4, AnalisisMulti, Cliente, Estandar, MetodoAnalisis, Muestra, MuestraMasificada, Proyecto, User , AnalisisCuTFeZn,ODT
from .forms import AnalisisCuS4FeS4MoS4Form, AnalisisCuTFeZnForm, AnalisisMultiForm, ClienteForm, CustomUserCreationForm, EstandarForm, MetodoAnalisisForm, MuestraForm, ODTForm, ProyectoForm
from django.views.decorators.csrf import csrf_exempt
from .decorators import is_administrador, is_supervisor, is_quimico

from django.db import transaction




@api_view(['POST'])
def logout_user(request):
    try:
        # Cerrar sesión del usuario
        logout(request)
        print("Usuario deslogueado correctamente")

        # Opcional: Limpiar el token si estás manejando la autenticación basada en tokens
        if hasattr(request.user, 'token'):
            request.user.token = None
            request.user.save()
            print("Token eliminado del usuario")

        return JsonResponse({'tipo': 'success', 'message': 'Deslogueo exitoso.'}, status=200)

    except Exception as e:
        print(f"Error al desloguear usuario: {e}")
        message = f"Error al desloguear usuario: {str(e)}"
        return JsonResponse({'tipo': 'error', 'message': message}, status=500)


@api_view(['GET'])
def users_list(request):
    try:
        users = User.objects.all()
        users_list = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'rolname': user.rolname,
                'turno': user.turno,
                'token': user.token,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
            }
            users_list.append(user_dict)
        return JsonResponse({'users': users_list})
    except Exception as e:
        logger.error("Error fetching user list: %s", e)
        return JsonResponse({'message': 'Error al obtener usuarios'}, status=500)
    
@api_view(['GET'])
def clientes_list(request):
    try:
        clientes = Cliente.objects.all()
        cliente_list = []
        for cliente in clientes:
            user_dict = {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'rut': cliente.rut,
                'direccion': cliente.direccion,
                'telefono': cliente.telefono,
                'email': cliente.email,
            }
            cliente_list.append(user_dict)
        return JsonResponse({'clientes': cliente_list})
    except Exception as e:
        logger.error("Error fetching user list: %s", e)
        return JsonResponse({'message': 'Error al obtener usuarios'}, status=500)


@api_view(['POST'])
def register_cliente(request):
    if request.method == 'POST':
        data = request.POST
        form = ClienteForm(data)
     
        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    # Obtener el registro existente para actualizarlo
                    usuario = Cliente.objects.get(pk=data['id'])
                    form = ClienteForm(data, instance=usuario)
                    form.save()
                    message = f"Cliente actualizado correctamente"
                else:
                    # Crear un nuevo registro
                    cliente = form.save()
                    cliente.save()
                    message = f"Cliente creado correctamente"
                return JsonResponse({'message': message, 'tipo': 'success'})
            except ValidationError  as e:
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f": {error}")
                return JsonResponse({'tipo': 'error', 'message': 'Error al crear cliente', 'errors': e})
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f": {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al crear cliente', 'errors': errors})
    else:
        return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})
    
@api_view(['GET'])
def proyectos_list(request):
    try:
        proyectos = Proyecto.objects.all()
        proyecto_list = []
        for proyecto in proyectos:
            proyecto_dict = {
                'id': proyecto.id,
                'nombre': proyecto.nombre,
                'cliente': {
                    'id': proyecto.cliente.id,  
                    'nombre': proyecto.cliente.nombre  
                },
                'fecha_emision': proyecto.fecha_emision,
            }
            proyecto_list.append(proyecto_dict)
        return JsonResponse({'proyectos': proyecto_list})
    except Exception as e:
        logger.error("Error fetching user list: %s", e)
        return JsonResponse({'message': 'Error al obtener proyectos'}, status=500)


@api_view(['POST'])
def register_proyectos(request):
    if request.method == 'POST':
        data = request.POST
        form = ProyectoForm(data)
     
        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    # Obtener el registro existente para actualizarlo
                    proyecto = Proyecto.objects.get(pk=data['id'])
                    form = ProyectoForm(data, instance=proyecto)
                    form.save()
                    message = f"Proyecto actualizado correctamente"
                else:
                    # Crear un nuevo registro
                    proyecto = form.save()
                    proyecto.save()
                    message = f"Proyecto creado correctamente"
                return JsonResponse({'message': message, 'tipo': 'success'})
            except ValidationError  as e:
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f": {error}")
                return JsonResponse({'tipo': 'error', 'message': 'Error al crear proyecto', 'errors': e})
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f": {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al crear proyecto', 'errors': errors})
    else:
        return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})


@api_view(['POST'])
def login_user(request):
    try:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is None:
                return JsonResponse({'error': 'El usuario o la contraseña ingresada son incorrectas'}, status=400)
            login(request, user)
            token=generar_token(user.id)
            user.token=token
            user.save()
            first_name = user.first_name
            last_name = user.last_name
            email = user.username
            token = user.token
            message=last_name
             
            return JsonResponse({'tipo':'success','message':message, 'first_name': first_name,'last_name':last_name,'email':email, 'token':token})
        else:
            message='El usuario o la contraseña ingresada son incorrectas'
            return JsonResponse({'tipo':'error','message':message }, status=400)
    except Exception as e:
        message="Error al loguear usuario:"
        return JsonResponse({'tipo':'error','message':message}, status=500)
   
def generar_token(user_id):
    expiracion = datetime.utcnow() + timedelta(days=1)
    token_data = {
        'user_id': user_id,
        'exp': expiracion.timestamp()
    }
    token = signing.dumps(token_data, key=settings.SECRET_KEY)
    return token

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        data = request.POST
        form = CustomUserCreationForm(data)
     
        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    # Obtener el registro existente para actualizarlo
                    usuario = User.objects.get(pk=data['id'])
                    form = CustomUserCreationForm(data, instance=usuario)
                    form.save()
                    message = f"Usuario actualizado correctamente"
                else:
                    # Crear un nuevo registro
                    user = form.save()
                    user.save()
                    message = f"Usuario creado correctamente"
                
                return JsonResponse({'message': message, 'tipo': 'success'})
            
            except ValidationError as e:
                return JsonResponse({'tipo': 'error', 'message': f'Error de validación: {str(e)}'})

        else:
            # Generar errores más específicos
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = list(field_errors)  
                message = f"Error al crear usuario: {errors}"

                return JsonResponse({'tipo': 'error', 'message': message, 'errors': errors})
    else:
        return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})

  
@api_view(['DELETE'])
def users_delete(request, id):
    try:
        user = get_object_or_404(User, id=id)
        user.delete()
        return JsonResponse({'message': 'Usuario eliminado con éxito'}, status=200)
    except Exception as e:
        logger.error("Error deleting user: %s", e)
        return JsonResponse({'message': 'Error al eliminar usuario'}, status=500)
        
    
    # LABORATORIO
def laboratorio(request):
    return render(request, 'hola')

@api_view(['GET'])
def muestras(request):
        muestras = Muestra.objects.all()
        muestra_list = []
        try:
            for muestra in muestras:
                muestra_dict = {
                    'id': muestra.id,
                    'proyecto': muestra.proyecto.nombre,
                    'nombre': muestra.nombre,
                    'fecha_emision': muestra.fecha_emision,
                    'elemento': muestra.elemento,
                    'nbo': muestra.nbo,
                    'ident': muestra.ident,
                    't': muestra.t,
                    'peso_m': muestra.peso_m,
                    'v_ml': muestra.v_ml,
                    'l_ppm': muestra.l_ppm,
                    'l_ppm_bk': muestra.l_ppm_bk,
                    'porcentaje': muestra.porcentaje,
                    
                }
                muestra_list.append(muestra_dict)
            return JsonResponse({'muestras': muestra_list})
        except Exception as e:
            logger.error("Error fetching user list: %s", e)
            return JsonResponse({'message': 'Error al obtener muestras'}, status=500)

@api_view(['POST'])
def register_muestra(request):
    if request.method == 'POST':
        data = request.POST
        form = MuestraForm(data)
      
        if form.is_valid():
            try: 
                muestra = form.save()
                muestra.save()
                nombre=muestra.nombre
                message = f"Muestra creada correctamente: {nombre}"
                return JsonResponse({'message': message, 'tipo': 'success'})
            except ValidationError  as e:
                message = f"Error al crear la muestra: {str(e)}"
                return JsonResponse({'message': message, 'tipo': 'error'})
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al crear la muestra', 'errors': errors})
    else:
        return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})

@api_view(['POST'])
def register_CutFeZn(request):
    if request.method == 'POST':
        data = request.POST
        form = AnalisisCuTFeZnForm(data)
     
        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    # Obtener el registro existente para actualizarlo
                    analisis = AnalisisCuTFeZn.objects.get(pk=data['id'])
                    form = AnalisisCuTFeZnForm(data, instance=analisis)
                    form.save()
                    message = f"Validador actualizado correctamente: Cut-Fe-Zn"
                else:
                    # Crear un nuevo registro
                    analisis = form.save()
                    message = f"Validador creado correctamente: Cut-Fe-Zn"

                return JsonResponse({'message': message, 'tipo': 'success'})

            except ValidationError as e:
                message = f"Error al procesar la muestra: {str(e)}"
                return JsonResponse({'message': message, 'tipo': 'error'})

            except AnalisisCuTFeZn.DoesNotExist:
                return JsonResponse({'message': 'El registro no existe.', 'tipo': 'error'})

        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al procesar el validador', 'errors': errors})

    return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})

@api_view(['POST'])
def register_CuS4FeS4MoS4(request):
    if request.method == 'POST':
        data = request.POST
        form = AnalisisCuS4FeS4MoS4Form(data)
     
        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    # Obtener el registro existente para actualizarlo
                    analisis = AnalisisCuS4FeS4MoS4.objects.get(pk=data['id'])
                    form = AnalisisCuS4FeS4MoS4Form(data, instance=analisis)
                    form.save()
                    message = f"Validador actualizado correctamente: CuS4-FeS4-MoS4"
                else:
                    # Crear un nuevo registro
                    analisis = form.save()
                    message = f"Validador creado correctamente: CuS4-FeS4-MoS4"

                return JsonResponse({'message': message, 'tipo': 'success'})

            except ValidationError as e:
                message = f"Error al procesar la muestra: {str(e)}"
                return JsonResponse({'message': message, 'tipo': 'error'})

            except AnalisisCuTFeZn.DoesNotExist:
                return JsonResponse({'message': 'El registro no existe.', 'tipo': 'error'})
            
@api_view(['POST'])
def register_Multi(request):
    if request.method == 'POST':
        data = request.POST
        form = AnalisisMultiForm(data)
     
        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    # Obtener el registro existente para actualizarlo
                    analisis = AnalisisMulti.objects.get(pk=data['id'])
                    form = AnalisisMultiForm(data, instance=analisis)
                    form.save()
                    message = f"Validador actualizado correctamente: Multi"
                else:
                    # Crear un nuevo registro
                    analisis = form.save()
                    message = f"Validador creado correctamente: Multi"

                return JsonResponse({'message': message, 'tipo': 'success'})

            except ValidationError as e:
                message = f"Error al procesar la muestra: {str(e)}"
                return JsonResponse({'message': message, 'tipo': 'error'})

            except AnalisisCuTFeZn.DoesNotExist:
                return JsonResponse({'message': 'El registro no existe.', 'tipo': 'error'})

        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al procesar el validador', 'errors': errors})

    return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})



@api_view(['POST'])
def register_ODT(request):
    if request.method == 'POST':
        data = request.data  

        print("Datos recibidos en el backend:", data)  # Para verificar si los datos están llegando correctamente.

        form = ODTForm(data)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear un nuevo registro dentro de una transacción atómica
                    odt = form.save()
                    message = "Orden de trabajo creada correctamente"
                    return JsonResponse({'message': message, 'tipo': 'success'}, status=201)

            except ValidationError as e:
                message = f"Error al procesar el registro: {str(e)}"
                print("Validation Error:", e)  # Mostrar detalles del error de validación
                return JsonResponse({'message': message, 'tipo': 'error'}, status=400)

        else:
            # Loguear errores del formulario y devolverlos al frontend
            print("Errores de validación del formulario:", form.errors)
            return JsonResponse({'tipo': 'error', 'message': 'Error en la validación del formulario', 'errors': form.errors}, status=400)

    return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'}, status=405)




@api_view(['POST'])
def register_Estandar(request):
    if request.method == 'POST':
        data = request.data  
        
        form = EstandarForm(data)
        
        if form.is_valid():
            try:
                # Crear un nuevo registro
                estandar = form.save()
                message = "Estandar creado correctamente"
                return JsonResponse({'message': message, 'tipo': 'success'}, status=201)

            except ValidationError as e:
                message = f"Error al procesar el registro: {str(e)}"
                return JsonResponse({'message': message, 'tipo': 'error'}, status=400)

        else:
            # Loguear errores del formulario y devolverlos al frontend
            return JsonResponse({'tipo': 'error', 'message': 'Error en la validación del formulario', 'errors': form.errors}, status=400)





 #GETS

@api_view(['GET'])
def CutFeZn(request):
        cutfezn = AnalisisCuTFeZn.objects.all()
        cutfezn_list = []
        try:
            for Cutfezn in cutfezn:
                cutfezn_dict = {
                    'id': Cutfezn.id,
                    'l_ppm_fe': Cutfezn.l_ppm_fe,
                    'l_ppm_bk_fe': Cutfezn.l_ppm_bk_fe,
                    'fe': Cutfezn.fe,
                    'l_ppm_zn': Cutfezn.l_ppm_zn,
                    'l_ppm_bk_zn': Cutfezn.l_ppm_bk_zn,
                    'zn': Cutfezn.zn
                }
                cutfezn_list.append(cutfezn_dict)
            return JsonResponse({'validacion': cutfezn_list})
        except Exception as e:
            logger.error("Error fetching validation list: %s", e)
            return JsonResponse({'message': 'Error al obtener la validación'}, status=500)

@api_view(['GET'])
def CuS4FeS4MoS4(request):
        CuS4FeS4MoS4 = AnalisisCuS4FeS4MoS4.objects.all()
        CuS4FeS4MoS4_list = []
        try:
            for cuS4FeS4MoS4 in CuS4FeS4MoS4:
                CuS4FeS4MoS4_dict = {
                    'id': cuS4FeS4MoS4.id,
                    'control1_cut_cus': cuS4FeS4MoS4.control1_cut_cus,
                    'l_ppm_cus_fe': cuS4FeS4MoS4.l_ppm_cus_fe,
                    'l_ppm_bk_fes4': cuS4FeS4MoS4.l_ppm_bk_fes4,
                    'fes4': cuS4FeS4MoS4.fes4,
                    'control2_cut_fes4': cuS4FeS4MoS4.control2_cut_fes4,
                }
                CuS4FeS4MoS4_list.append(CuS4FeS4MoS4_dict)
            return JsonResponse({'validacion': CuS4FeS4MoS4_list})
        except Exception as e:
            logger.error("Error fetching validation list: %s", e)
            return JsonResponse({'message': 'Error al obtener la validación'}, status=500)

@api_view(['GET'])
def Multi(request):
        Multi = AnalisisMulti.objects.all()
        Multi_list = []
        try:
            for multi in Multi:
                Multi_dict = {
                    'id': multi.id,
                    'l_ppm_ag': multi.l_ppm_ag,
                    'l_ppm_ag_bk': multi.l_ppm_ag_bk,
                    'ag': multi.ag,
                    'l_ppm_as': multi.l_ppm_as,
                    'l_ppm_as_bk': multi.l_ppm_as_bk,
                    'analisis_as': multi.analisis_as,
                    'l_ppm_mo': multi.l_ppm_mo,
                    'l_ppm_mo_bk': multi.l_ppm_mo_bk,
                    'mo': multi.mo,
                    'l_ppm_pb': multi.l_ppm_pb,
                    'l_ppm_pb_bk': multi.l_ppm_pb_bk,
                    'pb': multi.pb,
                    'l_ppm_cu': multi.l_ppm_cu,
                    'l_ppm_cu_bk': multi.l_ppm_cu_bk,
                    'cu': multi.cu,
                }
                Multi_list.append(Multi_dict)
            return JsonResponse({'validacion': Multi_list})
        except Exception as e:
            logger.error("Error fetching validation list: %s", e)
            return JsonResponse({'message': 'Error al obtener la validación'}, status=500)

@api_view(['GET'])
def get_ODT(request):
    try:
        odt = ODT.objects.select_related('Cliente', 'Proyecto').all()
        odt_list = []
        for item in odt:
            odt_dict = {
                'id': item.id,
                'fecha_emision': item.Fec_Recep,
                'fecha_entrega': item.Fec_Finalizacion,
                'Prefijo': item.Prefijo,
                'cliente': item.Cliente.nombre if item.Cliente else "Cliente no asignado",
                'proyecto': item.Proyecto.nombre if item.Proyecto else "Proyecto no asignado",
                'Responsable': item.Responsable,
                'Prioridad': item.Prioridad,
                'TipoMuestra': item.TipoMuestra,
                'Referencia': item.Referencia,
                'Cant_Muestra': item.Cant_Muestra,
            }
            odt_list.append(odt_dict)
        return JsonResponse({'odt': odt_list})
    except Exception as e:
        logger.error("Error fetching validation list: %s", e)
        return JsonResponse({'message': 'Error al obtener la orden de trabajo'}, status=500)

@api_view(['GET'])
def get_ODTDetails(request, id):
    try:
        muestraM = MuestraMasificada.objects.select_related('odt').filter(odt=id)
        muestraM_list = []

        for item in muestraM:
            muestraM_dict = {
                'odt': item.odt.id,
                'cliente': item.odt.Cliente.nombre,
                'Prefijo': item.Prefijo,
                'fecha_creacion': item.fecha_creacion,
                'tipoMuestra': item.tipoMuestra,
            }
            muestraM_list.append(muestraM_dict)

        return JsonResponse({'muestraM': muestraM_list}, safe=False)
    except Exception as e:
        logger.error("Error fetching muestra masificada: %s", e)
        return JsonResponse({'message': 'Error al obtener la muestra masificada'}, status=500)
    


@api_view(['GET'])
def get_method(request):
    try:
        method = MetodoAnalisis.objects.select_related('cliente').prefetch_related('elementos').all()
        method_list = []

        for item in method:
            elementos_list = []
            for elemento in item.elementos.all():
                elementos_list.append({
                    'id': elemento.id,
                    'nombre': elemento.nombre,
                    'gramos': elemento.gramos,
                    'miligramos': elemento.miligramos,
                })

            method_dict = {
                'id': item.id,
                'cliente': item.cliente.nombre,
                'nombre': item.nombre,
                'metodologia': item.metodologia,
                'elementos': elementos_list,
            }
            method_list.append(method_dict)

        return JsonResponse({'metodo': method_list}, safe=False)
    except Exception as e:
        logger.error("Error fetching elemento: %s", e)
        return JsonResponse({'message': 'Error al obtener el metodo'}, status=500)




@api_view(['GET'])
def get_metodos_agrupados(request):
    try:
        # Obtener todos los métodos de análisis, con los elementos relacionados
        metodos = MetodoAnalisis.objects.select_related('cliente').prefetch_related('elementos').all()

        # Agrupar los métodos por cliente
        agrupados_por_cliente = {}
        for metodo in metodos:
            cliente_nombre = metodo.cliente.nombre
            if cliente_nombre not in agrupados_por_cliente:
                agrupados_por_cliente[cliente_nombre] = []

            # Agregar el método a la lista de métodos del cliente
            metodo_data = {
                'metodoanalisis_id': metodo.id,
                'nombre': metodo.nombre,
                'metodologia': metodo.metodologia,
                'elementos': [
                    {
                        'elementometodo_id': elemento.id,
                        'nombre': elemento.nombre,
                        'gramos': elemento.gramos,
                        'miligramos': elemento.miligramos
                    }
                    for elemento in metodo.elementos.all()
                ]
            }
            agrupados_por_cliente[cliente_nombre].append(metodo_data)

        return JsonResponse({'data': agrupados_por_cliente}, status=200)

    except Exception as e:
        return JsonResponse({'message': f'Error: {str(e)}', 'tipo': 'error'}, status=500)


@api_view(['GET'])
def get_Estandar(request):
    try:
        estandar=Estandar.objects.all()
        estandar_list = []

        for item in estandar:
            estandar_dict = {
                'id': item.id,
                'cliente': item.cliente,
                'Unidad': item.Unidad,
                'VA': item.VA,
                'DS': item.DS,
                'Min': item.Min,
                'Max': item.Max,
            }
            estandar_list.append(estandar_dict)

        return JsonResponse({'estandar': estandar_list}, safe=False)
    except Exception as e:
        logger.error("Error fetching estandar: %s", e)
        return JsonResponse({'message': 'Error al obtener el estandar'}, status=500)