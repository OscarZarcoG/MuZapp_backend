from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Client
from .serializers import ClientSerializer
from core.exceptions import NotFoundError, ValidationError

class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar clientes
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo_cliente', 'frecuencia', 'ciudad', 'is_active']
    search_fields = ['nombre', 'apellidos', 'email', 'telefono', 'empresa']
    ordering_fields = ['nombre', 'apellidos', 'created_at', 'frecuencia']
    ordering = ['nombre', 'apellidos']
    
    def get_queryset(self):
        """Personalizar queryset según parámetros"""
        queryset = super().get_queryset()
        
        # Filtrar por activos por defecto
        if self.request.query_params.get('include_inactive') != 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_destroy(self, instance):
        """Soft delete del cliente"""
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar un cliente eliminado"""
        try:
            client = Client.objects.all_with_deleted().get(pk=pk)
            if not client.is_deleted():
                return Response(
                    {'detail': 'El cliente no está eliminado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            client.restore()
            serializer = self.get_serializer(client)
            return Response(serializer.data)
        except Client.DoesNotExist:
            raise NotFoundError('Cliente no encontrado')
    
    @action(detail=False, methods=['get'])
    def active_clients(self, request):
        """Obtener solo clientes activos"""
        queryset = Client.objects.active_clients()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def frequent_clients(self, request):
        """Obtener clientes frecuentes"""
        queryset = Client.objects.filter(frecuencia='frecuente', is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def companies(self, request):
        """Obtener solo empresas y organizaciones"""
        queryset = Client.objects.filter(
            tipo_cliente__in=['empresa', 'organizacion'],
            is_active=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
