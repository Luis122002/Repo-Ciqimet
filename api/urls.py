from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.login),
    path('index/',views.Main),
    path('AddODT/',views.AddODT),
    path('ODT/',views.ODT_Module)
]
