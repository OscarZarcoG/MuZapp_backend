from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar el router para las vistas del API
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)
router.register(r'equipos-audio', views.EquipoAudioViewSet)
router.register(r'catering', views.CateringViewSet)
router.register(r'peticiones', views.PeticionViewSet)
router.register(r'repertorio', views.RepertorioViewSet)
router.register(r'fotos-evento', views.FotosEventoViewSet)
router.register(r'contratos', views.ContratoViewSet)

urlpatterns = [
    path('agenda/', include(router.urls)),
]