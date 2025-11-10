from functools import wraps
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect

# Constantes de roles
ADMIN = 'administrador'
SUPERVISOR = 'supervisor'
CLIENTE = 'cliente'
QUIMICO_A = 'quimico_A'
QUIMICO_B = 'quimico_B'
QUIMICO_C = 'quimico_C'

QUIMICOS = [QUIMICO_A, QUIMICO_B, QUIMICO_C]
ADMIN_Y_SUPERVISOR = [ADMIN, SUPERVISOR]
ADMIN_Y_QUIMICOS = [ADMIN] + QUIMICOS
TODOS_LOS_QUIMICOS = QUIMICOS
TODOS = [ADMIN, SUPERVISOR] + QUIMICOS

# Decorador general para un solo rol
def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rolname == required_role:
                return view_func(request, *args, **kwargs)
            messages.error(request, f'No tienes permisos de {required_role}')
            return redirect('/')
        return wrapped_view
    return decorator

# Decorador para múltiples roles
def roles_required(required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rolname in required_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes los permisos necesarios para acceder a esta página.')
            return redirect('/index/')
        return wrapped_view
    return decorator

# Decoradores individuales
def is_administrador(view_func):
    return role_required(ADMIN)(view_func)

def is_supervisor(view_func):
    return role_required(SUPERVISOR)(view_func)

def is_cliente(view_func):
    return role_required(CLIENTE)(view_func)

def is_quimico_a(view_func):
    return role_required(QUIMICO_A)(view_func)

def is_quimico_b(view_func):
    return role_required(QUIMICO_B)(view_func)

def is_quimico_c(view_func):
    return role_required(QUIMICO_C)(view_func)

# Decoradores combinados
def is_administrador_or_supervisor(view_func):
    return roles_required(ADMIN_Y_SUPERVISOR)(view_func)

def is_all_quimicos(view_func):
    return roles_required(QUIMICOS)(view_func)

def is_full_acceso(view_func):
    return roles_required(TODOS)(view_func)

def is_internal_user(view_func):
    return roles_required([ADMIN, SUPERVISOR] + QUIMICOS)(view_func)
