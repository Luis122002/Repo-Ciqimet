from django.urls import path
from . import views


urlpatterns = [
    path('', views.requestAcces, name="Acces"),
    path('register/', views.login),
    path('index/', views.Main, name='index'),  # Asegúrate de definir 'index'
    path('AddODT/', views.AddODT),
    path('ODT/', views.ODT_Module),
    path('ODT-info/', views.ODT_Info),
    
    path('Action-Resource/<str:token>/', views.general_form, name='general_form'),

    path('Elements-Manager/', views.Elements_Section, name='elements_manager'),
    path('Analisis-Manager/', views.Elements_Section, name='analisis_manager'),
    path('Puesto-trabajo/', views.PT_Module),
    path('Puesto-instrumental/', views.PI_Module),

    path('MasterData/', views.Master_def, name='master_def'),
]