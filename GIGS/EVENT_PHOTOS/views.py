from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import EventPhoto
from .serializers import (
    EventPhotoSerializer,
    EventPhotoListSerializer,
    EventPhotoCreateSerializer,
    EventPhotoUpdateSerializer,
    EventPhotoActionSerializer,
    EventPhotoStatsSerializer
)


class EventPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de fotos de eventos"""
    
    queryset = EventPhoto.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros
    filterset_fields = {
        'tipo_evento': ['exact', 'in'],
        'publicas': ['exact'],
        'destacadas': ['exact'],
        'fecha_evento': ['exact', 'gte', 'lte', 'year', 'month'],
        'fecha_foto': ['exact', 'gte', 'lte', 'year', 'month'],
        'cliente': ['exact'],
        'contrato': ['exact'],
        'fotografo': ['exact', 'icontains'],
    }
    
    # Búsqueda
    search_fields = [
        'nombre_foto', 'evento', 'descripcion', 'ubicacion',
        'fotografo', 'cliente__nombre', 'cliente__apellido'
    ]
    
    # Ordenamiento
    ordering_fields = [
        'fecha_evento', 'fecha_foto', 'nombre_foto', 'evento',
        'tipo_evento', 'created_at', 'updated_at'
    ]
    ordering = ['-fecha_evento', '-fecha_foto']
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'list':
            return EventPhotoListSerializer
        elif self.action == 'create':
            return EventPhotoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EventPhotoUpdateSerializer
        elif self.action in ['photo_action']:
            return EventPhotoActionSerializer
        elif self.action == 'statistics':
            return EventPhotoStatsSerializer
        return EventPhotoSerializer
    
    def get_queryset(self):
        """Optimizar queryset con select_related"""
        return EventPhoto.objects.select_related(
            'cliente', 'contrato'
        ).prefetch_related(
            'cliente__telefono_set'
        )
    
    def perform_destroy(self, instance):
        """Soft delete - marcar como inactivo"""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
    
    # Acciones personalizadas para filtros
    
    @action(detail=False, methods=['get'])
    def public_photos(self, request):
        """Obtener fotos públicas"""
        photos = self.get_queryset().filter(publicas=True)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured_photos(self, request):
        """Obtener fotos destacadas"""
        photos = self.get_queryset().filter(destacadas=True)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_event_type(self, request):
        """Obtener fotos por tipo de evento"""
        event_type = request.query_params.get('tipo_evento')
        if not event_type:
            return Response(
                {'error': 'Debe especificar el parámetro tipo_evento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photos = self.get_queryset().filter(tipo_evento=event_type)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_client(self, request):
        """Obtener fotos por cliente"""
        client_id = request.query_params.get('cliente_id')
        if not client_id:
            return Response(
                {'error': 'Debe especificar el parámetro cliente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photos = self.get_queryset().filter(cliente_id=client_id)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_contract(self, request):
        """Obtener fotos por contrato"""
        contract_id = request.query_params.get('contrato_id')
        if not contract_id:
            return Response(
                {'error': 'Debe especificar el parámetro contrato_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photos = self.get_queryset().filter(contrato_id=contract_id)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Obtener fotos en un rango de fechas"""
        start_date = request.query_params.get('fecha_inicio')
        end_date = request.query_params.get('fecha_fin')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Debe especificar fecha_inicio y fecha_fin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photos = self.get_queryset().filter(
            fecha_evento__gte=start_date,
            fecha_evento__lte=end_date
        )
        
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_photographer(self, request):
        """Obtener fotos por fotógrafo"""
        photographer = request.query_params.get('fotografo')
        if not photographer:
            return Response(
                {'error': 'Debe especificar el parámetro fotografo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photos = self.get_queryset().filter(fotografo__icontains=photographer)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtener fotos recientes"""
        days = int(request.query_params.get('dias', 30))
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        photos = self.get_queryset().filter(created_at__date__gte=cutoff_date)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = EventPhotoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    # Acciones sobre fotos individuales
    
    @action(detail=True, methods=['post'])
    def photo_action(self, request, pk=None):
        """Realizar acciones sobre una foto"""
        photo = self.get_object()
        serializer = EventPhotoActionSerializer(data=request.data)
        
        if serializer.is_valid():
            accion = serializer.validated_data['accion']
            
            if accion == 'destacar':
                photo.marcar_como_destacada()
                message = 'Foto marcada como destacada'
            elif accion == 'quitar_destacada':
                photo.quitar_destacada()
                message = 'Foto removida de destacadas'
            elif accion == 'hacer_publica':
                photo.hacer_publica()
                message = 'Foto marcada como pública'
            elif accion == 'hacer_privada':
                photo.hacer_privada()
                message = 'Foto marcada como privada'
            
            return Response({
                'message': message,
                'photo': EventPhotoSerializer(photo).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def restore(self, request, pk=None):
        """Restaurar foto eliminada (soft delete)"""
        try:
            # Buscar en fotos eliminadas
            photo = EventPhoto.objects.filter(id=pk, is_active=False).first()
            if not photo:
                return Response(
                    {'error': 'Foto no encontrada o no está eliminada'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            photo.is_active = True
            photo.save(update_fields=['is_active', 'updated_at'])
            
            return Response({
                'message': 'Foto restaurada exitosamente',
                'photo': EventPhotoSerializer(photo).data
            })
        
        except Exception as e:
            return Response(
                {'error': f'Error al restaurar la foto: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Estadísticas
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas de fotos"""
        queryset = self.get_queryset()
        
        # Estadísticas generales
        total_fotos = queryset.count()
        fotos_publicas = queryset.filter(publicas=True).count()
        fotos_destacadas = queryset.filter(destacadas=True).count()
        fotos_privadas = queryset.filter(publicas=False).count()
        eventos_con_fotos = queryset.values('evento').distinct().count()
        fotografos_activos = queryset.exclude(
            fotografo__isnull=True
        ).exclude(
            fotografo=''
        ).values('fotografo').distinct().count()
        
        # Tamaño total en MB
        tamaño_total = queryset.aggregate(
            total=Sum('tamaño_archivo')
        )['total'] or 0
        tamaño_total_mb = round(tamaño_total / (1024 * 1024), 2)
        
        # Estadísticas por tipo de evento
        por_tipo_evento = {}
        for choice in EventPhoto.TIPO_EVENTO_CHOICES:
            tipo_key = choice[0]
            tipo_label = choice[1]
            count = queryset.filter(tipo_evento=tipo_key).count()
            if count > 0:
                por_tipo_evento[tipo_label] = count
        
        # Estadísticas mensuales (últimos 12 meses)
        por_mes = []
        for i in range(12):
            fecha = timezone.now().date().replace(day=1) - timedelta(days=30*i)
            count = queryset.filter(
                fecha_evento__year=fecha.year,
                fecha_evento__month=fecha.month
            ).count()
            por_mes.append({
                'mes': fecha.strftime('%Y-%m'),
                'nombre_mes': fecha.strftime('%B %Y'),
                'fotos': count
            })
        
        # Top fotógrafos
        top_fotografos = list(
            queryset.exclude(
                fotografo__isnull=True
            ).exclude(
                fotografo=''
            ).values('fotografo').annotate(
                total_fotos=Count('id')
            ).order_by('-total_fotos')[:10]
        )
        
        stats_data = {
            'total_fotos': total_fotos,
            'fotos_publicas': fotos_publicas,
            'fotos_destacadas': fotos_destacadas,
            'fotos_privadas': fotos_privadas,
            'eventos_con_fotos': eventos_con_fotos,
            'fotografos_activos': fotografos_activos,
            'tamaño_total_mb': tamaño_total_mb,
            'por_tipo_evento': por_tipo_evento,
            'por_mes': por_mes,
            'top_fotografos': top_fotografos
        }
        
        serializer = EventPhotoStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def event_types(self, request):
        """Obtener tipos de eventos disponibles"""
        return Response({
            'tipos_evento': [
                {'value': choice[0], 'label': choice[1]}
                for choice in EventPhoto.TIPO_EVENTO_CHOICES
            ]
        })
    
    @action(detail=False, methods=['get'])
    def photographers(self, request):
        """Obtener lista de fotógrafos"""
        photographers = self.get_queryset().exclude(
            fotografo__isnull=True
        ).exclude(
            fotografo=''
        ).values_list('fotografo', flat=True).distinct().order_by('fotografo')
        
        return Response({
            'fotografos': list(photographers)
        })
