from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count, Case, When, IntegerField
from .models import ClientRequest
from .serializers import (
    ClientRequestSerializer,
    ClientRequestListSerializer,
    ClientRequestActionSerializer
)


class ClientRequestViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar peticiones de clientes"""
    
    queryset = ClientRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtros
    filterset_fields = {
        'estado': ['exact', 'in'],
        'prioridad': ['exact', 'in'],
        'cliente': ['exact'],
        'evento_relacionado': ['exact'],
        'fecha_solicitud': ['gte', 'lte', 'exact'],
        'fecha_necesaria': ['gte', 'lte', 'exact'],
        'dificultad_estimada': ['exact', 'in'],
        'genero': ['exact', 'icontains'],
    }
    
    # Búsqueda
    search_fields = [
        'nombre_cancion',
        'artista',
        'album',
        'genero',
        'cliente__nombre',
        'cliente__apellidos',
        'evento_relacionado__titulo',
        'notas_cliente',
    ]
    
    # Ordenamiento
    ordering_fields = [
        'fecha_solicitud',
        'fecha_necesaria',
        'prioridad',
        'estado',
        'nombre_cancion',
        'artista',
    ]
    ordering = ['-fecha_solicitud']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return ClientRequestListSerializer
        elif self.action in ['approve', 'reject', 'mark_in_repertoire']:
            return ClientRequestActionSerializer
        return ClientRequestSerializer
    
    def get_queryset(self):
        """Personaliza el queryset base"""
        queryset = super().get_queryset()
        
        # Incluir información relacionada para optimizar consultas
        queryset = queryset.select_related(
            'cliente',
            'evento_relacionado'
        )
        
        return queryset
    
    def perform_destroy(self, instance):
        """Soft delete - marca como eliminado"""
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtiene peticiones pendientes"""
        queryset = self.get_queryset().filter(estado='pendiente')
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def approved(self, request):
        """Obtiene peticiones aprobadas"""
        queryset = self.get_queryset().filter(estado='aprobada')
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Obtiene peticiones urgentes"""
        queryset = self.get_queryset().filter(prioridad='urgente')
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_client(self, request):
        """Obtiene peticiones por cliente"""
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response(
                {'error': 'Se requiere el parámetro cliente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(cliente_id=cliente_id)
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_event(self, request):
        """Obtiene peticiones por evento"""
        evento_id = request.query_params.get('evento_id')
        if not evento_id:
            return Response(
                {'error': 'Se requiere el parámetro evento_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(evento_relacionado_id=evento_id)
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba una petición"""
        instance = self.get_object()
        
        if instance.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden aprobar peticiones pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            notas_internas = serializer.validated_data.get('notas_internas', '')
            instance.aprobar(notas_internas)
            
            response_serializer = ClientRequestSerializer(instance)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechaza una petición"""
        instance = self.get_object()
        
        if instance.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden rechazar peticiones pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'action': 'reject'}
        )
        if serializer.is_valid():
            motivo_rechazo = serializer.validated_data.get('motivo_rechazo')
            instance.rechazar(motivo_rechazo)
            
            response_serializer = ClientRequestSerializer(instance)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_in_repertoire(self, request, pk=None):
        """Marca una petición como agregada al repertorio"""
        instance = self.get_object()
        
        if instance.estado != 'aprobada':
            return Response(
                {'error': 'Solo se pueden marcar como repertorio peticiones aprobadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.marcar_en_repertorio()
        
        serializer = ClientRequestSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaura una petición eliminada"""
        # Obtener incluyendo eliminados
        try:
            instance = ClientRequest.objects.all_with_deleted().get(pk=pk)
        except ClientRequest.DoesNotExist:
            return Response(
                {'error': 'Petición no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if instance.deleted_at is None:
            return Response(
                {'error': 'La petición no está eliminada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.deleted_at = None
        instance.is_active = True
        instance.save()
        
        serializer = ClientRequestSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtiene estadísticas de peticiones"""
        queryset = self.get_queryset()
        
        # Estadísticas por estado
        stats_by_status = queryset.aggregate(
            total=Count('id'),
            pendientes=Count(Case(When(estado='pendiente', then=1), output_field=IntegerField())),
            aprobadas=Count(Case(When(estado='aprobada', then=1), output_field=IntegerField())),
            rechazadas=Count(Case(When(estado='rechazada', then=1), output_field=IntegerField())),
            en_repertorio=Count(Case(When(estado='en_repertorio', then=1), output_field=IntegerField())),
        )
        
        # Estadísticas por prioridad
        stats_by_priority = queryset.aggregate(
            urgentes=Count(Case(When(prioridad='urgente', then=1), output_field=IntegerField())),
            altas=Count(Case(When(prioridad='alta', then=1), output_field=IntegerField())),
            medias=Count(Case(When(prioridad='media', then=1), output_field=IntegerField())),
            bajas=Count(Case(When(prioridad='baja', then=1), output_field=IntegerField())),
        )
        
        # Peticiones próximas a vencer (fecha necesaria en los próximos 7 días)
        from datetime import date, timedelta
        proximas_vencer = queryset.filter(
            fecha_necesaria__lte=date.today() + timedelta(days=7),
            fecha_necesaria__gte=date.today(),
            estado__in=['pendiente', 'aprobada']
        ).count()
        
        return Response({
            'por_estado': stats_by_status,
            'por_prioridad': stats_by_priority,
            'proximas_vencer': proximas_vencer,
        })
