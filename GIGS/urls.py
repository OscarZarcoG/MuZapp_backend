from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar el router para las vistas del API
router = DefaultRouter()
router.register(r'clientes', views.ClientViewSet)
router.register(r'equipos-audio', views.AudioEquipmentViewSet)
router.register(r'catering', views.CateringViewSet)
router.register(r'peticiones', views.ClientRequestViewSet)
router.register(r'repertorio', views.RepertorioViewSet)
router.register(r'fotos-evento', views.EventPhotoViewSet)
router.register(r'contratos', views.ContractViewSet)

urlpatterns = [
    path('agenda/', include(router.urls)),
]