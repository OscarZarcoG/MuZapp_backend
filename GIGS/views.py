from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta

from .models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato
from .serializers import (
    ClienteSerializer, EquipoAudioSerializer, CateringSerializer,
    PeticionSerializer, RepertorioSerializer, FotosEventoSerializer,
    ContratoSerializer, ContratoCreateSerializer, ContratoListSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar clientes"""
    queryset = Cliente.objects.filter(is_active=True)
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['frecuencia', 'tipo_cliente']
    search_fields = ['nombre', 'apellidos', 'telefono', 'email', 'empresa']
    ordering_fields = ['nombre', 'apellidos', 'frecuencia', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar cliente eliminado"""
        cliente = self.get_object()
        cliente.restore()
        return Response({'status': 'Cliente restaurado'})


class EquipoAudioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar equipos de audio"""
    queryset = Equipo_Audio.objects.filter(is_active=True)
    serializer_class = EquipoAudioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'marca', 'ubicacion']
    search_fields = ['nombre', 'marca', 'modelo', 'numero_serie', 'descripcion', 'observaciones']
    ordering_fields = ['nombre', 'tipo', 'estado', 'marca', 'modelo', 'precio_compra', 'fecha_compra', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar equipo eliminado"""
        equipo = self.get_object()
        equipo.restore()
        return Response({'status': 'Equipo restaurado'})

    @action(detail=False, methods=['get'])
    def por_precio(self, request):
        """Filtrar equipos por rango de precio"""
        precio_min = request.query_params.get('precio_min', 0)
        precio_max = request.query_params.get('precio_max', 999999)
        
        # Usar precio_compra en lugar de precio
        equipos = self.queryset.filter(
            precio_compra__gte=precio_min,
            precio_compra__lte=precio_max
        )
        
        serializer = self.get_serializer(equipos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Filtrar equipos por estado"""
        estado = request.query_params.get('estado')
        if estado:
            equipos = self.queryset.filter(estado=estado)
            serializer = self.get_serializer(equipos, many=True)
            return Response(serializer.data)
        return Response({'error': 'Estado requerido'}, status=400)

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Filtrar equipos por tipo"""
        tipo = request.query_params.get('tipo')
        if tipo:
            equipos = self.queryset.filter(tipo=tipo)
            serializer = self.get_serializer(equipos, many=True)
            return Response(serializer.data)
        return Response({'error': 'Tipo requerido'}, status=400)


class CateringViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar catering"""
    queryset = Catering.objects.filter(is_active=True)
    serializer_class = CateringSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['peticion_grupo']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class PeticionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar peticiones"""
    queryset = Peticion.objects.filter(is_active=True)
    serializer_class = PeticionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_cancion']
    ordering_fields = ['nombre_cancion', 'created_at']
    ordering = ['-created_at']


class RepertorioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar repertorio"""
    queryset = Repertorio.objects.filter(is_active=True)
    serializer_class = RepertorioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_cancion']
    ordering_fields = ['nombre_cancion', 'created_at']
    ordering = ['nombre_cancion']


class FotosEventoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar fotos de eventos"""
    queryset = Fotos_Evento.objects.filter(is_active=True)
    serializer_class = FotosEventoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fecha_foto']
    search_fields = ['nombre_foto']
    ordering_fields = ['nombre_foto', 'fecha_foto', 'created_at']
    ordering = ['-fecha_foto']

    @action(detail=False, methods=['get'])
    def por_mes(self, request):
        """Obtener fotos por mes y año"""
        año = request.query_params.get('año', timezone.now().year)
        mes = request.query_params.get('mes', timezone.now().month)
        
        fotos = self.queryset.filter(
            fecha_foto__year=año,
            fecha_foto__month=mes
        )
        
        serializer = self.get_serializer(fotos, many=True)
        return Response(serializer.data)


class ContratoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar contratos"""
    queryset = Contrato.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado_evento', 'tipo_evento', 'fecha_evento', 'cliente']
    search_fields = ['numero_contrato', 'titulo', 'nombre_festejado', 'cliente__nombre_cliente']
    ordering_fields = ['fecha_evento', 'hora_inicio', 'pago_total', 'created_at']
    ordering = ['-fecha_evento']

    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'create':
            return ContratoCreateSerializer
        elif self.action == 'list':
            return ContratoListSerializer
        return ContratoSerializer

    @action(detail=False, methods=['get'])
    def proximos_eventos(self, request):
        """Obtener eventos próximos (próximos 30 días)"""
        fecha_limite = timezone.now().date() + timedelta(days=30)
        contratos = self.queryset.filter(
            fecha_evento__gte=timezone.now().date(),
            fecha_evento__lte=fecha_limite,
            estado_evento__in=['pending', 'confirmed']
        ).order_by('fecha_evento', 'hora_inicio')
        
        serializer = ContratoListSerializer(contratos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def eventos_hoy(self, request):
        """Obtener eventos de hoy"""
        hoy = timezone.now().date()
        contratos = self.queryset.filter(fecha_evento=hoy)
        
        serializer = ContratoListSerializer(contratos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de contratos"""
        total_contratos = self.queryset.count()
        pendientes = self.queryset.filter(estado_evento='pending').count()
        confirmados = self.queryset.filter(estado_evento='confirmed').count()
        en_progreso = self.queryset.filter(estado_evento='in_progress').count()
        completados = self.queryset.filter(estado_evento='completed').count()
        cancelados = self.queryset.filter(estado_evento='cancelled').count()
        
        # Ingresos del mes actual
        mes_actual = timezone.now().date().replace(day=1)
        ingresos_mes = self.queryset.filter(
            fecha_evento__gte=mes_actual,
            estado_evento='completed'
        ).aggregate(
            total=models.Sum('pago_total')
        )['total'] or 0
        
        return Response({
            'total_contratos': total_contratos,
            'pendientes': pendientes,
            'confirmados': confirmados,
            'en_progreso': en_progreso,
            'completados': completados,
            'cancelados': cancelados,
            'ingresos_mes_actual': ingresos_mes
        })

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar un contrato"""
        contrato = self.get_object()
        contrato.estado_evento = 'cancelled'
        contrato.save()
        
        serializer = self.get_serializer(contrato)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar un contrato (cuando se recibe adelanto)"""
        contrato = self.get_object()
        adelanto = request.data.get('adelanto', 0)
        
        if adelanto > 0:
            contrato.pago_adelanto = adelanto
            contrato.estado_evento = 'confirmed'
            contrato.save()
            
            serializer = self.get_serializer(contrato)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'El adelanto debe ser mayor a 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        """Generar contrato en PDF usando ReportLab (rápido)"""
        contrato = self.get_object()
        try:
            response = contrato.generar_contrato_pdf()
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def generar_docx(self, request, pk=None):
        """Generar contrato en DOCX"""
        contrato = self.get_object()
        try:
            response = contrato.generar_contrato_docx()
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar DOCX: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )