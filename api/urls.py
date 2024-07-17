from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.login),
    path('index/',views.Main),
    path('ODT/',views.ODT_Module)
]
