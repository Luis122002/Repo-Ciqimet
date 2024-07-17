from functools import wraps
from django.http import JsonResponse


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
