from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet

# Router para las rutas del ViewSet
router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs disponibles:
# GET /contracts/ - Listar contratos
# POST /contracts/ - Crear contrato
# GET /contracts/{id}/ - Obtener contrato específico
# PUT /contracts/{id}/ - Actualizar contrato completo
# PATCH /contracts/{id}/ - Actualizar contrato parcial
# DELETE /contracts/{id}/ - Eliminar contrato (soft delete)

# Acciones personalizadas:
# GET /contracts/pending/ - Contratos pendientes
# GET /contracts/confirmed/ - Contratos confirmados
# GET /contracts/in_progress/ - Contratos en progreso
# GET /contracts/completed/ - Contratos completados
# GET /contracts/upcoming/ - Contratos próximos
# GET /contracts/this_week/ - Contratos de esta semana
# GET /contracts/this_month/ - Contratos de este mes
# GET /contracts/by_client/?cliente_id=X - Contratos por cliente
# GET /contracts/by_date_range/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD - Contratos por rango de fechas
# POST /contracts/{id}/confirm/ - Confirmar contrato
# POST /contracts/{id}/start/ - Iniciar contrato
# POST /contracts/{id}/complete/ - Completar contrato
# POST /contracts/{id}/cancel/ - Cancelar contrato
# POST /contracts/{id}/restore/ - Restaurar contrato eliminado
# GET /contracts/statistics/ - Estadísticas de contratos
# POST /contracts/validate_schedule/ - Validar conflictos de horario