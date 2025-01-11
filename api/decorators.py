from functools import wraps
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect

def is_administrador(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        print(request.user)
        
    
        return JsonResponse({'error': 'No tienes permisos de administrador'}, status=403)
    return wrapped_view

def is_supervisor(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_supervisor:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'No tienes permisos de supervisor'}, status=403)
    return wrapped_view

def is_quimico(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_quimico:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'No tienes permisos de quimico'}, status=403)
    return wrapped_view

def is_cliente(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_cliente:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'error': 'No tienes permisos de cliente'}, status=403)
    return wrapped_view








def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rolname == required_role:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'No tienes permisos de {required_role}')
                return redirect('/')
        return wrapped_view
    return decorator

def roles_required(required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rolname in required_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'No tienes los permisos necesarios para acceder a esta página.')
                return redirect('/index/') 
        return wrapped_view
    return decorator

def is_administrador_project(view_func):
    return role_required('Administrador')(view_func)

def is_quimico_project(view_func):
    return role_required('Quimico')(view_func)

def is_supervisor_project(view_func):
    return role_required('Supervisor')(view_func)

def is_administrador_or_quimico(view_func):
    return roles_required(['Administrador', 'Quimico'])(view_func)

def is_administrador_or_supervisor(view_func):
    return roles_required(['Administrador', 'Supervisor'])(view_func)