from django.urls import path
from . import views, viewsReact


urlpatterns = [


    path('', views.Sitio_Web),

       # USUARIOS
    path('api/unlogin/', viewsReact.logout_user, name='logout'),
    path('api/register/', viewsReact.register_user, name='register'),
    path('api/login/', viewsReact.login_user, name='login'),
    path('api/users/', viewsReact.users_list, name='users'),
    path('api/users/delete/<int:id>/', viewsReact.users_delete, name='users_delete'),
    
    # CLIENTE
    path('api/clientes/', viewsReact.clientes_list, name='clientes'),
    path('api/registerCliente/', viewsReact.register_cliente, name='register_cliente'),
    
    # PROYECTOS
    path('api/proyectos/', viewsReact.proyectos_list, name='proyectos'),
    path('api/registerProyectos/', viewsReact.register_proyectos, name='register_proyectos'),
    
    # GESTION LABORATORIO
    path('api/laboratorio/', viewsReact.laboratorio, name='laboratorio'),
    path('api/muestras/', viewsReact.muestras, name='muestras'),
    path('api/registerMuestra/', viewsReact.register_muestra, name='register_muestra'),
    path('api/CuTFeZn/', viewsReact.CutFeZn, name='CutFeZn'),
    path('api/registerCuTFeZn/', viewsReact.register_CutFeZn, name='register_CutFeZn'),
    path('api/CuS4FeS4MoS4/', viewsReact.CuS4FeS4MoS4, name='CuS4FeS4MoS4'),
    path('api/registerCuS4FeS4MoS4/', viewsReact.register_CuS4FeS4MoS4, name='register_CuS4FeS4MoS4'),
    path('api/Multi/', viewsReact.Multi, name='multi'),
    path('api/registerMulti/', viewsReact.register_Multi, name='register_Multi'),
    
    # ODT
    path('api/registerODT/', viewsReact.register_ODT, name='registerODT'),
    path('api/ODT/', viewsReact.get_ODT, name='get_ODT'),
    path('api/ODTDetails/<str:id>/', viewsReact.get_ODTDetails, name='get_ODTDetails'),
   
   # TRABAJO/Metodo de analisis
    path('api/method/', viewsReact.get_method, name='method'),
    
    #Estandar de empresa
    path('registerEstandar/', viewsReact.register_Estandar, name='registerEstandar'),
    path('Estandar/', viewsReact.get_Estandar, name='get_Estandar'),


    path('login/', views.login_view, name='login_View'),
    path('unlogin/', views.logout_View, name='logout_View'),
    
    
    path('index/', views.Main, name='index'),

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



    path('Tester-balanza/', views.tester_balanza, name='tester_balanza'),
    path('api/list-usb-ports/', views.list_usb_ports, name='list_usb_ports'),
    path('api/get-events/', views.get_events, name='get_events'),


]