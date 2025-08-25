from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepertorioViewSet

# Router para las URLs del repertorio
router = DefaultRouter()
router.register(r'repertorio', RepertorioViewSet, basename='repertorio')

urlpatterns = [
    path('', include(router.urls)),
]

# URLs disponibles:
# GET /repertorio/ - Lista todas las canciones del repertorio
# POST /repertorio/ - Crea una nueva canción
# GET /repertorio/{id}/ - Obtiene una canción específica
# PUT /repertorio/{id}/ - Actualiza una canción completa
# PATCH /repertorio/{id}/ - Actualiza parcialmente una canción
# DELETE /repertorio/{id}/ - Elimina una canción (soft delete)
#
# Acciones personalizadas:
# GET /repertorio/favorites/ - Obtiene canciones favoritas
# GET /repertorio/by_genre/?genero=rock - Filtra por género
# GET /repertorio/by_artist/?artista=queen - Filtra por artista
# GET /repertorio/by_duration/?min_duracion=180&max_duracion=300 - Filtra por duración
# GET /repertorio/with_links/ - Canciones con enlaces
# GET /repertorio/without_links/ - Canciones sin enlaces
# GET /repertorio/recent/?dias=30 - Canciones recientes
# GET /repertorio/popular/ - Canciones más populares
# POST /repertorio/{id}/song_action/ - Ejecuta acciones sobre una canción
# POST /repertorio/restore/ - Restaura canciones eliminadas
# GET /repertorio/statistics/ - Estadísticas del repertorio
# GET /repertorio/genres/ - Lista de géneros disponibles
# GET /repertorio/artists/ - Lista de artistas disponibles
# GET /repertorio/search_songs/ - Búsqueda avanzada de canciones