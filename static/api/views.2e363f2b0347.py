from asyncio.log import logger
from django.conf import settings
from django.core import signing
from datetime import datetime, timedelta
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import User
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_exempt
from .decorators import is_administrador, is_supervisor, is_quimico, is_cliente

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
                'is_cliente': user.is_cliente,
                'is_new_user': user.is_new_user,
                'date_joined': user.date_joined,
            }
            users_list.append(user_dict)
        return JsonResponse({'users': users_list})
    except Exception as e:
        logger.error("Error fetching user list: %s", e)
        return JsonResponse({'message': 'Error al obtener usuarios'}, status=500)

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
            token = user.token
            message=last_name
             
            return JsonResponse({'tipo':'success','message':message, 'first_name': first_name,'token':token})
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try: 
                user = form.save()
                first_name = user.first_name
                date_joined = user.date_joined.date()  
                current_date = datetime.now().date()
                if (current_date - date_joined).days < 30:
                    is_new_user=user.is_new_user = True
                    user.save()
                else:
                    is_new_user=user.is_new_user = False
                    user.save()
                message = f"Usuario creado correctamente: {first_name}"
                return JsonResponse({'message': message, 'tipo': 'success', 'is_new_user': is_new_user})
            except ValidationError  as e:
                message = f"Error al crear usuario: {str(e)}"
                return JsonResponse({'message': message, 'tipo': 'error'})
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f": {error}")
            return JsonResponse({'tipo': 'error', 'message': 'Error al crear usuario', 'errors': errors})
    else:
        return JsonResponse({'tipo': 'error', 'message': 'Método no permitido. Utiliza el método POST.'})
