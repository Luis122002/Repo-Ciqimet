from django.urls import path
from . import views


urlpatterns = [
    path('', views.requestAcces, name="Acces"),
    path('login/', views.login_view, name='login'),
    path('index/', views.Main, name='index'),  # Asegúrate de definir 'index'
    path('ODT/', views.ODT_Module, name='Main_ODT'),
    path('ODT-info/', views.ODT_Info),
    path('ODT-info_Request/', views.ODT_Info_Request),
    
    path('Action-Resource/<str:token>/', views.general_form, name='general_form'),
    path('Action-Resource/<str:token>/Action-Resource/', views.general_form),

    path('ModMuestra/', views.ModMuestras),
    path('ModODT/', views.ModODT),
    path('get-proyectos/', views.get_proyectos, name='get_proyectos'),

    path('Elements-Manager/', views.Elements_Section, name='elements_manager'),
    path('Analisis-Manager/', views.Elements_Section, name='analisis_manager'),
    path('Puesto-trabajo/', views.PT_Module),
    path('Puesto-instrumental/', views.PI_Module),

    path('MasterData/', views.Master_def, name='master_def'),
]