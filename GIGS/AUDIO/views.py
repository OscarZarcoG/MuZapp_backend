# GIGS/AUDIO/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import AudioEquipment
from .serializers import AudioEquipmentSerializer

class AudioEquipmentViewSet(viewsets.ModelViewSet):
    queryset = AudioEquipment.objects.all()
    serializer_class = AudioEquipmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'marca', 'ubicacion']
    search_fields = ['nombre', 'marca', 'modelo', 'numero_serie', 'descripcion']
    ordering_fields = ['nombre', 'marca', 'modelo', 'fecha_compra', 'precio_compra', 'created_at']
    ordering = ['nombre']
    
    def perform_destroy(self, instance):
        """Soft delete - marcar como eliminado en lugar de eliminar físicamente"""
        instance.soft_delete()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Obtener equipos disponibles"""
        available_equipment = self.queryset.filter(estado='disponible', is_active=True)
        serializer = self.get_serializer(available_equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Obtener equipos por tipo"""
        tipo = request.query_params.get('tipo')
        if not tipo:
            return Response(
                {'error': 'Parámetro "tipo" es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipment = self.queryset.filter(tipo=tipo, is_active=True)
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def maintenance_needed(self, request):
        """Obtener equipos que necesitan mantenimiento"""
        maintenance_equipment = self.queryset.filter(
            estado__in=['mantenimiento', 'averiado'], 
            is_active=True
        )
        serializer = self.get_serializer(maintenance_equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_in_use(self, request, pk=None):
        """Marcar equipo como en uso"""
        equipment = self.get_object()
        if equipment.marcar_en_uso():
            return Response(
                {'message': 'Equipo marcado como en uso'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No se puede marcar el equipo como en uso'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):
        """Marcar equipo como disponible"""
        equipment = self.get_object()
        if equipment.marcar_disponible():
            return Response(
                {'message': 'Equipo marcado como disponible'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No se puede marcar el equipo como disponible'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def restore(self, request):
        """Restaurar equipos eliminados (soft delete)"""
        equipment_id = request.query_params.get('id')
        if not equipment_id:
            return Response(
                {'error': 'Parámetro "id" es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            equipment = AudioEquipment.all_objects.get(id=equipment_id)
            equipment.restore()
            serializer = self.get_serializer(equipment)
            return Response(
                {
                    'message': 'Equipo restaurado exitosamente',
                    'equipment': serializer.data
                }, 
                status=status.HTTP_200_OK
            )
        except AudioEquipment.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas de equipos"""
        total_equipment = self.queryset.count()
        available_count = self.queryset.filter(estado='disponible').count()
        in_use_count = self.queryset.filter(estado='en_uso').count()
        maintenance_count = self.queryset.filter(estado__in=['mantenimiento', 'averiado']).count()
        
        # Estadísticas por tipo
        type_stats = {}
        for tipo_code, tipo_name in AudioEquipment.TIPO_EQUIPO_CHOICES:
            type_stats[tipo_name] = self.queryset.filter(tipo=tipo_code).count()
        
        return Response({
            'total_equipment': total_equipment,
            'available': available_count,
            'in_use': in_use_count,
            'maintenance_needed': maintenance_count,
            'by_type': type_stats
        })
