"""
URL configuration for ServiciosWebTransporte project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from funcionalidades.views import*


urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/', inicio),
    path('validarUbicacion/', validar_ubicacion),
    path('paradaCercana/', parada_cercana),
    path('rutaCercana/', ruta_cercana),
    path('paradaRadio/', parada_radio),
    path('rutaRadio/', ruta_radio),
    path('pos_omnibus/', obtener_posiciones),
    path('seleccionar_destino/', seleccionar_destino, name='seleccionar_destino'),
    path('crear_ruta_personalizada/', crear_ruta_personalizada, name='crear_ruta_personalizada'),
    #path('data/', geojson_data),
]
