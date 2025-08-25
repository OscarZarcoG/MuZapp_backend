from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientRequestViewSet

# Router para las vistas basadas en ViewSet
router = DefaultRouter()
router.register(r'requests', ClientRequestViewSet, basename='clientrequest')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs disponibles:
# GET /requests/ - Lista todas las peticiones
# POST /requests/ - Crea una nueva petición
# GET /requests/{id}/ - Obtiene una petición específica
# PUT /requests/{id}/ - Actualiza una petición completa
# PATCH /requests/{id}/ - Actualiza parcialmente una petición
# DELETE /requests/{id}/ - Elimina (soft delete) una petición
#
# Acciones personalizadas:
# GET /requests/pending/ - Peticiones pendientes
# GET /requests/approved/ - Peticiones aprobadas
# GET /requests/urgent/ - Peticiones urgentes
# GET /requests/by_client/?cliente_id=X - Peticiones por cliente
# GET /requests/by_event/?evento_id=X - Peticiones por evento
# POST /requests/{id}/approve/ - Aprobar petición
# POST /requests/{id}/reject/ - Rechazar petición
# POST /requests/{id}/mark_in_repertoire/ - Marcar como en repertorio
# POST /requests/{id}/restore/ - Restaurar petición eliminada
# GET /requests/statistics/ - Estadísticas de peticiones