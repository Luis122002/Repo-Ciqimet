from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.login),
    path('index/',views.Main),
    path('AddODT/',views.AddODT),
    path('ODT/',views.ODT_Module),
    path('ODT-info/', views.ODT_Info),
    path('Puesto-trabajo/',views.PT_Module),
    path('Puesto-instrumental/',views.PI_Module)
]
