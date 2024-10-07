from django.urls import path
from . import views, viewsReact


urlpatterns = [


    path('', views.requestAcces, name="Acces"),

    # USUARIOS
    path('api/register/', viewsReact.register_user, name='register'),
    path('api/login/', viewsReact.login_user, name='login'),
    path('api/unlogin/', viewsReact.logout_user, name='logout'),

    path('api/users/', viewsReact.users_list, name='users'),
    path('api/users/delete/<int:id>/', viewsReact.users_delete, name='users_delete'),


    path('login/', views.login_view, name='login_View'),
    path('unlogin/', views.logout_View, name='logout_View'),
    
    
    path('index/', views.Main, name='index'),

    path('ODT/', views.ODT_Module, name='Main_ODT'),
    path('ODT-info/', views.ODT_Info),
    path('ODT-info_Request/', views.ODT_Info_Request),
    
    path('Action-Resource/<str:token>/', views.general_form, name='general_form'),
    path('Action-Resource/<str:token>/Action-Resource/', views.general_form),

    path('ModMuestra/', views.ModMuestras),
    path('ModODT/', views.ModODT),
    path('get-proyectos/', views.get_proyectos, name='get_proyectos'),

    path('Elements-Manager/', views.Elements_Section, name='elements_manager'),
    path('Analysis-Manager/', views.Analysis_Section, name='analisis_manager'),


    path('MasterData/', views.Master_def, name='master_def'),

    path('Puesto-trabajo/', views.PT_Module),
    path('Balanza/', views.Balanza_Module),
    path('Puesto-Absorcion/', views.PI_Module),
    path('Hoja-Trabajo/', views.HT_Module),

    path('api/status/', views.check_db_connection, name='check_db_connection'),
    path('api/get-user-data/', views.get_user_data, name='get_user_data'),
]