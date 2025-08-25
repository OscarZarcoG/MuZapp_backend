from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventPhotoViewSet

# Router para las URLs del ViewSet
router = DefaultRouter()
router.register(r'event-photos', EventPhotoViewSet, basename='eventphoto')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs disponibles:
# GET /event-photos/ - Listar fotos
# POST /event-photos/ - Crear nueva foto
# GET /event-photos/{id}/ - Obtener foto específica
# PUT /event-photos/{id}/ - Actualizar foto completa
# PATCH /event-photos/{id}/ - Actualizar foto parcial
# DELETE /event-photos/{id}/ - Eliminar foto (soft delete)
#
# Acciones personalizadas:
# GET /event-photos/public_photos/ - Fotos públicas
# GET /event-photos/featured_photos/ - Fotos destacadas
# GET /event-photos/by_event_type/?tipo_evento=X - Fotos por tipo de evento
# GET /event-photos/by_client/?cliente_id=X - Fotos por cliente
# GET /event-photos/by_contract/?contrato_id=X - Fotos por contrato
# GET /event-photos/by_date_range/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD - Fotos por rango de fechas
# GET /event-photos/by_photographer/?fotografo=X - Fotos por fotógrafo
# GET /event-photos/recent/?dias=X - Fotos recientes (últimos X días, default 30)
# POST /event-photos/{id}/photo_action/ - Realizar acción sobre foto (destacar, hacer pública, etc.)
# DELETE /event-photos/{id}/restore/ - Restaurar foto eliminada
# GET /event-photos/statistics/ - Estadísticas de fotos
# GET /event-photos/event_types/ - Tipos de eventos disponibles
# GET /event-photos/photographers/ - Lista de fotógrafos