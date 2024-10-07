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
from api.models import Cliente, Proyecto, User
from .forms import ClienteForm, CustomUserCreationForm
from django.views.decorators.csrf import csrf_exempt
from .decorators import is_administrador, is_supervisor, is_quimico

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
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_administrador': user.is_administrador,
                'is_supervisor': user.is_supervisor,
                'is_quimico': user.is_quimico,
                'is_new_user': user.is_new_user,
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
                return JsonResponse({'tipo': 'error', 'message': 'Error al crear usuario', 'errors': e})
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f": {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al crear usuario', 'errors': errors})
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
                    'id': proyecto.cliente.id,  # Aquí puedes ajustar los campos que necesitas del cliente
                    'nombre': proyecto.cliente.nombre  # Asegúrate de que el modelo Cliente tiene este campo
                },
                'fecha_emision': proyecto.fecha_emision,
            }
            proyecto_list.append(proyecto_dict)
        return JsonResponse({'proyectos': proyecto_list})
    except Exception as e:
        logger.error("Error fetching user list: %s", e)
        return JsonResponse({'message': 'Error al obtener proyectos'}, status=500)




@api_view(['POST'])
def login_user(request):
    try:
        print("Solicitud de inicio de sesión recibida")
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print("Formulario válido")
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is None:
                print("Usuario o contraseña incorrectos")
                return JsonResponse({'error': 'El usuario o la contraseña ingresada son incorrectas'}, status=400)
            
            # Autenticar y loguear al usuario
            print(f"Usuario autenticado: {user}")
            login(request, user)
            
            # Generar y asignar token al usuario
            token = generar_token(user.id)
            user.token = token
            user.save()
            print(f"Token generado y guardado: {token}")
            
            # Extraer datos del usuario para la respuesta
            first_name = user.first_name
            last_name = user.last_name
            email = user.username
            message = last_name
            
            return JsonResponse({'tipo':'success','message':message, 'first_name': first_name,'last_name':last_name,'email':email, 'token':token})
        else:
            print("Formulario inválido, error en datos ingresados")
            message = 'El usuario o la contraseña ingresada son incorrectas'
            return JsonResponse({'tipo':'error','message':message }, status=400)
    except Exception as e:
        print(f"Error al loguear usuario: {e}")
        message = f"Error al loguear usuario: {str(e)}"
        return JsonResponse({'tipo':'error','message':message}, status=500)
    

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
        print("Datos recibidos:", data)

        # Inicializa el formulario con los datos del request
        form = CustomUserCreationForm(data)
        print("Formulario inicializado:", form)

        if form.is_valid():
            try:
                # Verificar si se está enviando un ID para actualizar el registro existente
                if 'id' in data and data['id']:
                    print("Actualizando usuario con ID:", data['id'])
                    # Obtener el registro existente para actualizarlo
                    usuario = User.objects.get(pk=data['id'])
                    form = CustomUserCreationForm(data, instance=usuario)
                    form.save()
                    message = f"Usuario actualizado correctamente"
                    print("Usuario actualizado:", usuario)
                else:
                    # Crear un nuevo registro
                    print("Creando un nuevo usuario.")
                    user = form.save()
                    user.save()
                    message = f"Usuario creado correctamente"
                    print("Nuevo usuario creado:", user)
                
                return JsonResponse({'message': message, 'tipo': 'success'})
            
            except ValidationError as e:
                print("Error de validación al crear/actualizar el usuario:", e)
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        print(f"Error en el campo {field}: {error}")
                        errors.append(f": {error}")
                return JsonResponse({'tipo': 'error', 'message': 'Error al crear usuario', 'errors': errors})
            
            except User.DoesNotExist:
                print("El usuario con el ID proporcionado no existe:", data['id'])
                return JsonResponse({'tipo': 'error', 'message': 'El usuario no existe', 'errors': []})
            
            except Exception as e:
                print("Error inesperado:", e)
                return JsonResponse({'tipo': 'error', 'message': 'Error inesperado al crear usuario', 'errors': [str(e)]})
        
        else:
            print("Formulario inválido:", form.errors)
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    print(f"Error en el campo {field}: {error}")
                    errors.append(f": {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al crear usuario', 'errors': errors})
    
    else:
        print("Método no permitido:", request.method)
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
        
    