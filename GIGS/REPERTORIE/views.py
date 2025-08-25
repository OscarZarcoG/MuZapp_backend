from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import Repertorio
from .serializers import (
    RepertorioSerializer,
    RepertorioListSerializer,
    RepertorioCreateSerializer,
    RepertorioUpdateSerializer,
    RepertorioActionSerializer,
    RepertorioStatsSerializer,
    RepertorioSearchSerializer
)


class RepertorioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar el repertorio musical"""
    
    queryset = Repertorio.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Campos de búsqueda
    search_fields = ['nombre_cancion', 'artista', 'genero', 'etiquetas']
    
    # Campos de filtrado
    filterset_fields = {
        'genero': ['exact', 'icontains'],
        'dificultad': ['exact'],
        'artista': ['exact', 'icontains'],
        'es_favorita': ['exact'],
        'veces_tocada': ['exact', 'gte', 'lte'],
        'duracion_segundos': ['gte', 'lte'],
        'created_at': ['date', 'date__gte', 'date__lte'],
        'ultima_vez_tocada': ['date', 'date__gte', 'date__lte', 'isnull'],
    }
    
    # Campos de ordenamiento
    ordering_fields = [
        'nombre_cancion', 'artista', 'genero', 'dificultad', 
        'veces_tocada', 'duracion_segundos', 'created_at', 
        'ultima_vez_tocada', 'es_favorita'
    ]
    ordering = ['nombre_cancion', 'artista']
    
    def get_serializer_class(self):
        """Devuelve el serializer apropiado según la acción"""
        if self.action == 'list':
            return RepertorioListSerializer
        elif self.action == 'create':
            return RepertorioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RepertorioUpdateSerializer
        elif self.action in ['song_action']:
            return RepertorioActionSerializer
        elif self.action == 'statistics':
            return RepertorioStatsSerializer
        elif self.action == 'search':
            return RepertorioSearchSerializer
        return RepertorioSerializer
    
    def perform_destroy(self, instance):
        """Soft delete - marca como inactivo en lugar de eliminar"""
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.save()
    
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Obtiene las canciones favoritas"""
        queryset = self.get_queryset().filter(es_favorita=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """Obtiene canciones por género"""
        genero = request.query_params.get('genero')
        if not genero:
            return Response(
                {'error': 'El parámetro genero es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().por_genero(genero)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_artist(self, request):
        """Obtiene canciones por artista"""
        artista = request.query_params.get('artista')
        if not artista:
            return Response(
                {'error': 'El parámetro artista es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().por_artista(artista)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_duration(self, request):
        """Filtra canciones por rango de duración"""
        min_duracion = request.query_params.get('min_duracion')
        max_duracion = request.query_params.get('max_duracion')
        
        try:
            min_dur = int(min_duracion) if min_duracion else None
            max_dur = int(max_duracion) if max_duracion else None
        except ValueError:
            return Response(
                {'error': 'Los parámetros de duración deben ser números enteros'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().por_duracion(min_dur, max_dur)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_links(self, request):
        """Obtiene canciones que tienen enlaces"""
        queryset = self.get_queryset().con_link()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def without_links(self, request):
        """Obtiene canciones que no tienen enlaces"""
        queryset = self.get_queryset().sin_link()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtiene canciones agregadas recientemente"""
        dias = request.query_params.get('dias', 30)
        try:
            dias = int(dias)
        except ValueError:
            dias = 30
        
        queryset = self.get_queryset().recientes(dias)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Obtiene las canciones más populares"""
        queryset = self.get_queryset().populares()[:20]  # Top 20
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def song_action(self, request, pk=None):
        """Ejecuta acciones sobre una canción específica"""
        song = self.get_object()
        serializer = RepertorioActionSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            etiqueta = serializer.validated_data.get('etiqueta')
            
            if action == 'marcar_favorita':
                song.marcar_favorita()
                message = 'Canción marcada como favorita'
            elif action == 'quitar_favorita':
                song.quitar_favorita()
                message = 'Canción quitada de favoritas'
            elif action == 'marcar_tocada':
                song.marcar_como_tocada()
                message = 'Canción marcada como tocada'
            elif action == 'agregar_etiqueta':
                song.agregar_etiqueta(etiqueta)
                message = f'Etiqueta "{etiqueta}" agregada'
            elif action == 'quitar_etiqueta':
                song.quitar_etiqueta(etiqueta)
                message = f'Etiqueta "{etiqueta}" quitada'
            
            return Response({
                'message': message,
                'song': RepertorioSerializer(song).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def restore(self, request):
        """Restaura canciones eliminadas (soft delete)"""
        song_ids = request.data.get('song_ids', [])
        
        if not song_ids:
            return Response(
                {'error': 'Se requiere una lista de IDs de canciones'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restaurar canciones
        restored_count = Repertorio.objects.filter(
            id__in=song_ids, 
            is_active=False
        ).update(
            is_active=True, 
            deleted_at=None
        )
        
        return Response({
            'message': f'{restored_count} canciones restauradas',
            'restored_count': restored_count
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtiene estadísticas del repertorio"""
        queryset = self.get_queryset()
        
        # Estadísticas generales
        total_canciones = queryset.count()
        total_artistas = queryset.values('artista').distinct().count()
        total_generos = queryset.values('genero').distinct().count()
        
        # Canción más tocada
        cancion_mas_tocada_obj = queryset.order_by('-veces_tocada').first()
        cancion_mas_tocada = str(cancion_mas_tocada_obj) if cancion_mas_tocada_obj else 'N/A'
        
        # Artista más frecuente
        artista_mas_frecuente_data = queryset.values('artista').annotate(
            count=Count('artista')
        ).order_by('-count').first()
        artista_mas_frecuente = artista_mas_frecuente_data['artista'] if artista_mas_frecuente_data else 'N/A'
        
        # Género más popular
        genero_mas_popular_data = queryset.values('genero').annotate(
            count=Count('genero')
        ).order_by('-count').first()
        genero_mas_popular = genero_mas_popular_data['genero'] if genero_mas_popular_data else 'N/A'
        
        # Duración total
        duracion_total_segundos = queryset.aggregate(
            total=Sum('duracion_segundos')
        )['total'] or 0
        
        # Formatear duración total
        horas = duracion_total_segundos // 3600
        minutos = (duracion_total_segundos % 3600) // 60
        segundos = duracion_total_segundos % 60
        duracion_total_formateada = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        
        # Otras estadísticas
        canciones_favoritas = queryset.filter(es_favorita=True).count()
        canciones_sin_tocar = queryset.filter(veces_tocada=0).count()
        promedio_veces_tocada = queryset.aggregate(
            promedio=Avg('veces_tocada')
        )['promedio'] or 0
        
        # Distribución por género
        distribucion_generos = dict(
            queryset.values('genero').annotate(
                count=Count('genero')
            ).values_list('genero', 'count')
        )
        
        # Distribución por dificultad
        distribucion_dificultad = dict(
            queryset.values('dificultad').annotate(
                count=Count('dificultad')
            ).values_list('dificultad', 'count')
        )
        
        # Canciones recientes (últimos 30 días)
        fecha_limite = timezone.now() - timedelta(days=30)
        canciones_recientes = queryset.filter(created_at__gte=fecha_limite).count()
        
        # Top 10 canciones más tocadas
        top_canciones = queryset.order_by('-veces_tocada')[:10]
        
        # Canciones favoritas
        canciones_favoritas_lista = queryset.filter(es_favorita=True)[:10]
        
        stats_data = {
            'total_canciones': total_canciones,
            'total_artistas': total_artistas,
            'total_generos': total_generos,
            'cancion_mas_tocada': cancion_mas_tocada,
            'artista_mas_frecuente': artista_mas_frecuente,
            'genero_mas_popular': genero_mas_popular,
            'duracion_total_segundos': duracion_total_segundos,
            'duracion_total_formateada': duracion_total_formateada,
            'canciones_favoritas': canciones_favoritas,
            'canciones_sin_tocar': canciones_sin_tocar,
            'promedio_veces_tocada': round(promedio_veces_tocada, 2),
            'distribucion_generos': distribucion_generos,
            'distribucion_dificultad': distribucion_dificultad,
            'canciones_recientes': canciones_recientes,
            'top_canciones': RepertorioListSerializer(top_canciones, many=True).data,
            'canciones_favoritas_lista': RepertorioListSerializer(canciones_favoritas_lista, many=True).data,
        }
        
        return Response(stats_data)
    
    @action(detail=False, methods=['get'])
    def genres(self, request):
        """Obtiene la lista de géneros disponibles"""
        generos = self.get_queryset().values_list('genero', flat=True).distinct()
        return Response(list(generos))
    
    @action(detail=False, methods=['get'])
    def artists(self, request):
        """Obtiene la lista de artistas disponibles"""
        artistas = self.get_queryset().values_list('artista', flat=True).distinct()
        return Response(list(artistas))
    
    @action(detail=False, methods=['get'])
    def search_songs(self, request):
        """Búsqueda avanzada de canciones"""
        serializer = RepertorioSearchSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        # Aplicar filtros
        search = serializer.validated_data.get('search')
        if search:
            queryset = queryset.buscar(search)
        
        genero = serializer.validated_data.get('genero')
        if genero:
            queryset = queryset.filter(genero__icontains=genero)
        
        dificultad = serializer.validated_data.get('dificultad')
        if dificultad:
            queryset = queryset.filter(dificultad=dificultad)
        
        artista = serializer.validated_data.get('artista')
        if artista:
            queryset = queryset.filter(artista__icontains=artista)
        
        es_favorita = serializer.validated_data.get('es_favorita')
        if es_favorita is not None:
            queryset = queryset.filter(es_favorita=es_favorita)
        
        con_link = serializer.validated_data.get('con_link')
        if con_link is not None:
            if con_link:
                queryset = queryset.con_link()
            else:
                queryset = queryset.sin_link()
        
        min_duracion = serializer.validated_data.get('min_duracion')
        max_duracion = serializer.validated_data.get('max_duracion')
        if min_duracion or max_duracion:
            queryset = queryset.por_duracion(min_duracion, max_duracion)
        
        etiqueta = serializer.validated_data.get('etiqueta')
        if etiqueta:
            queryset = queryset.filter(etiquetas__icontains=etiqueta)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RepertorioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepertorioListSerializer(queryset, many=True)
        return Response(serializer.data)
