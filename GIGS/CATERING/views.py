# GIGS/CATERING/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Catering
from .serializers import CateringSerializer

class CateringViewSet(viewsets.ModelViewSet):
    queryset = Catering.objects.all()
    serializer_class = CateringSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'tipo_evento', 'proveedor']
    search_fields = ['peticion_grupo', 'tipo_evento', 'proveedor', 'ubicacion', 'notas_adicionales']
    ordering_fields = ['fecha_evento', 'presupuesto_estimado', 'numero_personas', 'created_at']
    ordering = ['-fecha_evento']
    
    def perform_destroy(self, instance):
        """Soft delete - marcar como eliminado en lugar de eliminar físicamente"""
        instance.soft_delete()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener solicitudes de catering pendientes"""
        pending_requests = self.queryset.filter(estado='pendiente', is_active=True)
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def confirmed(self, request):
        """Obtener solicitudes de catering confirmadas"""
        confirmed_requests = self.queryset.filter(estado='confirmado', is_active=True)
        serializer = self.get_serializer(confirmed_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_provider(self, request):
        """Obtener solicitudes por proveedor"""
        proveedor = request.query_params.get('proveedor')
        if not proveedor:
            return Response(
                {'error': 'Parámetro "proveedor" es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        requests = self.queryset.filter(proveedor__icontains=proveedor, is_active=True)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmar solicitud de catering"""
        catering = self.get_object()
        if catering.confirmar():
            return Response(
                {'message': 'Solicitud de catering confirmada'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No se puede confirmar la solicitud de catering'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar solicitud de catering"""
        catering = self.get_object()
        if catering.cancelar():
            return Response(
                {'message': 'Solicitud de catering cancelada'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No se puede cancelar la solicitud de catering'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar solicitud de catering"""
        catering = self.get_object()
        if catering.completar():
            return Response(
                {'message': 'Solicitud de catering completada'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No se puede completar la solicitud de catering'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def restore(self, request):
        """Restaurar solicitudes eliminadas (soft delete)"""
        catering_id = request.query_params.get('id')
        if not catering_id:
            return Response(
                {'error': 'Parámetro "id" es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            catering = Catering.all_objects.get(id=catering_id)
            catering.restore()
            serializer = self.get_serializer(catering)
            return Response(
                {
                    'message': 'Solicitud de catering restaurada exitosamente',
                    'catering': serializer.data
                }, 
                status=status.HTTP_200_OK
            )
        except Catering.DoesNotExist:
            return Response(
                {'error': 'Solicitud de catering no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas de catering"""
        total_requests = self.queryset.count()
        pending_count = self.queryset.filter(estado='pendiente').count()
        confirmed_count = self.queryset.filter(estado='confirmado').count()
        completed_count = self.queryset.filter(estado='completado').count()
        cancelled_count = self.queryset.filter(estado='cancelado').count()
        
        # Estadísticas por proveedor
        provider_stats = {}
        providers = self.queryset.exclude(proveedor='').values_list('proveedor', flat=True).distinct()
        for provider in providers:
            if provider:
                provider_stats[provider] = self.queryset.filter(proveedor=provider).count()
        
        return Response({
            'total_requests': total_requests,
            'pending': pending_count,
            'confirmed': confirmed_count,
            'completed': completed_count,
            'cancelled': cancelled_count,
            'by_provider': provider_stats
        })
