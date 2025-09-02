from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AudioConversionViewSet, HomeView, ConversionsListView

app_name = 'music'

# Crear el router y registrar el ViewSet
router = DefaultRouter()
router.register(r'conversions', AudioConversionViewSet, basename='audioconversion')

urlpatterns = [
    # Template views (interfaz web)
    path('', HomeView.as_view(), name='home'),
    path('conversions/', ConversionsListView.as_view(), name='conversions_list'),
    
    # API endpoints
    path('url/', include(router.urls)),
]

# Los endpoints disponibles serán:
# GET /conversions/ - Listar todas las conversiones
# POST /conversions/ - Crear nueva conversión
# GET /conversions/{id}/ - Obtener detalles de una conversión
# PUT /conversions/{id}/ - Actualizar conversión completa
# PATCH /conversions/{id}/ - Actualizar conversión parcial
# DELETE /conversions/{id}/ - Eliminar conversión
# POST /conversions/convert/ - Convertir audio desde URL
# GET /conversions/{id}/download/ - Descargar archivo de audio