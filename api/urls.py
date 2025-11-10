from django.urls import path
from . import views
from django.urls import path




urlpatterns = [


    path('', views.Sitio_Web),

    path('login/', views.login_view, name='login_View'),
    path('unlogin/', views.logout_View, name='logout_View'),
    
    
    path('index/', views.Main, name='index'),
    path('Inicio/', views.Sitio_Web, name='Inicio'),

    path('ODT/', views.ODT_Module, name='Main_ODT'),
    path('ODT-info/', views.ODT_Info, name='info_ODT'),
    
    path('Action-Resource/<str:token>/', views.general_form, name='general_form'),
    path('Action-Resource/<str:token>/Action-Resource/', views.general_form),

    path('get-proyectos/', views.get_proyectos, name='get_proyectos'),

    path('Elements-Manager/', views.Elements_Section, name='elements_manager'),
    path('Analysis-Manager/', views.Analysis_Section, name='analisis_manager'),


    path('MasterData/', views.Master_def, name='master_def'),
    path('Puesto-trabajo/', views.PT_Module),
    path('Balanza/', views.Balanza_Module, name='balanza_module'),

    path('Save-M/', views.Save_M),
    path('Confirm-M/', views.Confirm_M),

    path('Puesto-Absorcion/', views.PI_Module),
    path('Hoja-Trabajo/', views.HT_Module),
    path('Get-HDT/', views.Request_HT, name='obtener_informacion_hoja_trabajo'),
    path('obtener-hojas/', views.obtener_hojas_trabajo, name='obtener-hojas'),
    path('lot-generator/', views.Lot_Generator),
    path('get-lotes/', views.get_lotes, name='get_lotes'),
    path('delete-lote/', views.delete_lote, name='delete_lote'),
    path('guardar-valores-absorcion/',views.guardar_valores_absorción),

    path('api/status/', views.check_db_connection, name='check_db_connection'),
    path('api/get-user-data/', views.get_user_data, name='get_user_data'),

    path('Servicio/', views.servicios, name='Servicio'),
    path('Sobre-Nosotros/', views.sobre_nosostros, name='Sobre-Nosotros'),
    path('Recursos/', views.recursos, name='Recursos'),
    path('noticias/', views.noticias, name='noticias'),
    path('noticias/agregar/', views.agregar_noticia, name='agregar_noticia'),
    path('noticias/modificar/<int:noticia_id>/', views.modificar_noticia, name='modificar_noticia'),
    path('noticias/eliminar/<int:noticia_id>/', views.eliminar_noticia, name='eliminar_noticia'),
    path('Contacto/', views.contacto, name='Contacto'),



    path('users/', views.UserListView, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/modify/<int:user_id>/', views.modify_user, name='modify_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),


    path('perfil/', views.perfil, name='perfil'),
    path('perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),



    path('clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('proyectos/agregar/', views.agregar_proyecto, name='agregar_proyecto'),

    path('api/peso-balanza/', views.leer_peso_balanza),
    path('api/guardar-peso/', views.guardar_peso),
    path('muestras/', views.Balanza_Module, name='balanza_module'),
    path('api/verificar-balanza/', views.verificar_balanza),


    path('Ajustar_Muestras/', views.Ajustar_Muestras, name='Ajustar_Muestras'),
    path('crear-admin-secreto-123/', views.crear_admin),
]