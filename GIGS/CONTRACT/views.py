from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Contract
from .serializers import (
    ContractSerializer,
    ContractListSerializer,
    ContractActionSerializer,
    ContractCreateSerializer,
    ContractUpdateSerializer
)


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de contratos"""
    
    queryset = Contract.objects.select_related('cliente', 'equipo_audio', 'catering').prefetch_related('peticiones_cliente')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros
    filterset_fields = {
        'estado_evento': ['exact', 'in'],
        'tipo_evento': ['exact', 'in'],
        'fecha_evento': ['exact', 'gte', 'lte', 'range'],
        'cliente': ['exact'],
        'pago_total': ['gte', 'lte', 'range'],
        'audiencia': ['gte', 'lte', 'range'],
        'created_at': ['gte', 'lte', 'date', 'date__range'],
    }
    
    # Búsqueda
    search_fields = [
        'numero_contrato', 'titulo', 'nombre_festejado', 'nombre_lugar',
        'cliente__nombre', 'cliente__apellidos', 'cliente__email',
        'notas', 'descripcion_lugar'
    ]
    
    # Ordenamiento
    ordering_fields = [
        'fecha_evento', 'created_at', 'updated_at', 'pago_total',
        'audiencia', 'numero_contrato', 'estado_evento'
    ]
    ordering = ['-fecha_evento', '-created_at']
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'list':
            return ContractListSerializer
        elif self.action == 'create':
            return ContractCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContractUpdateSerializer
        elif self.action in ['confirm', 'start', 'complete', 'cancel']:
            return ContractActionSerializer
        return ContractSerializer
    
    def perform_destroy(self, instance):
        """Soft delete del contrato"""
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtener contratos pendientes"""
        contracts = self.get_queryset().pending()
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def confirmed(self, request):
        """Obtener contratos confirmados"""
        contracts = self.get_queryset().confirmed()
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        """Obtener contratos en progreso"""
        contracts = self.get_queryset().in_progress()
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Obtener contratos completados"""
        contracts = self.get_queryset().completed()
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Obtener contratos próximos"""
        contracts = self.get_queryset().upcoming()
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def this_week(self, request):
        """Obtener contratos de esta semana"""
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        
        contracts = self.get_queryset().by_date_range(start_week, end_week)
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def this_month(self, request):
        """Obtener contratos de este mes"""
        today = timezone.now().date()
        start_month = today.replace(day=1)
        if today.month == 12:
            end_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        contracts = self.get_queryset().by_date_range(start_month, end_month)
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_client(self, request):
        """Obtener contratos por cliente"""
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response(
                {'error': 'Se requiere el parámetro cliente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contracts = self.get_queryset().by_client(cliente_id)
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Obtener contratos en un rango de fechas"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Se requieren los parámetros start_date y end_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contracts = self.get_queryset().by_date_range(start_date, end_date)
        page = self.paginate_queryset(contracts)
        if page is not None:
            serializer = ContractListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmar contrato"""
        contract = self.get_object()
        serializer = ContractActionSerializer(data=request.data, context={'action': 'confirm'})
        
        if serializer.is_valid():
            try:
                notas = serializer.validated_data.get('notas', '')
                contract.confirmar(notas)
                return Response(
                    {'message': 'Contrato confirmado exitosamente'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar contrato (marcar como en progreso)"""
        contract = self.get_object()
        
        try:
            contract.iniciar()
            return Response(
                {'message': 'Contrato iniciado exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar contrato"""
        contract = self.get_object()
        serializer = ContractActionSerializer(data=request.data, context={'action': 'complete'})
        
        if serializer.is_valid():
            try:
                notas = serializer.validated_data.get('notas', '')
                contract.completar(notas)
                return Response(
                    {'message': 'Contrato completado exitosamente'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar contrato"""
        contract = self.get_object()
        serializer = ContractActionSerializer(data=request.data, context={'action': 'cancelar'})
        
        if serializer.is_valid():
            try:
                motivo = serializer.validated_data.get('motivo_cancelacion')
                contract.cancelar(motivo)
                return Response(
                    {'message': 'Contrato cancelado exitosamente'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restaurar contrato eliminado (soft delete)"""
        try:
            contract = Contract.objects.get(pk=pk, is_active=False)
            contract.is_active = True
            contract.save()
            
            serializer = ContractSerializer(contract)
            return Response(
                {
                    'message': 'Contrato restaurado exitosamente',
                    'contract': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Contract.DoesNotExist:
            return Response(
                {'error': 'Contrato no encontrado o ya está activo'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtener estadísticas de contratos"""
        queryset = self.get_queryset()
        
        # Estadísticas generales
        total_contracts = queryset.count()
        pending_contracts = queryset.pending().count()
        confirmed_contracts = queryset.confirmed().count()
        in_progress_contracts = queryset.in_progress().count()
        completed_contracts = queryset.completed().count()
        cancelled_contracts = queryset.cancelled().count()
        
        # Estadísticas financieras
        financial_stats = queryset.aggregate(
            total_revenue=Sum('pago_total'),
            total_advances=Sum('pago_adelanto'),
            average_contract_value=Avg('pago_total'),
            average_audience=Avg('audiencia')
        )
        
        # Contratos próximos (próximos 30 días)
        upcoming_30_days = queryset.filter(
            fecha_evento__gte=timezone.now().date(),
            fecha_evento__lte=timezone.now().date() + timedelta(days=30)
        ).count()
        
        # Contratos por tipo de evento
        event_types = queryset.values('tipo_evento').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Contratos por mes (últimos 12 meses)
        monthly_stats = []
        for i in range(12):
            date = timezone.now().date().replace(day=1) - timedelta(days=30*i)
            month_start = date.replace(day=1)
            if date.month == 12:
                month_end = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
            
            month_contracts = queryset.filter(
                fecha_evento__gte=month_start,
                fecha_evento__lte=month_end
            )
            
            monthly_stats.append({
                'month': date.strftime('%Y-%m'),
                'total_contracts': month_contracts.count(),
                'total_revenue': month_contracts.aggregate(Sum('pago_total'))['pago_total__sum'] or 0,
                'completed_contracts': month_contracts.completed().count()
            })
        
        return Response({
            'general': {
                'total_contracts': total_contracts,
                'pending_contracts': pending_contracts,
                'confirmed_contracts': confirmed_contracts,
                'in_progress_contracts': in_progress_contracts,
                'completed_contracts': completed_contracts,
                'cancelled_contracts': cancelled_contracts,
                'upcoming_30_days': upcoming_30_days
            },
            'financial': financial_stats,
            'event_types': list(event_types),
            'monthly_stats': monthly_stats[:12]  # Últimos 12 meses
        })
    
    @action(detail=False, methods=['post'])
    def validate_schedule(self, request):
        """Validar conflictos de horario"""
        fecha_evento = request.data.get('fecha_evento')
        hora_inicio = request.data.get('hora_inicio')
        hora_final = request.data.get('hora_final')
        contract_id = request.data.get('contract_id')  # Para excluir en ediciones
        
        if not all([fecha_evento, hora_inicio, hora_final]):
            return Response(
                {'error': 'Se requieren fecha_evento, hora_inicio y hora_final'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha_evento = datetime.strptime(fecha_evento, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio, '%H:%M:%S').time()
            hora_final = datetime.strptime(hora_final, '%H:%M:%S').time()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha/hora inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar conflictos
        conflicting_contracts = Contract.objects.filter(
            fecha_evento=fecha_evento,
            estado_evento__in=['confirmed', 'in_progress']
        )
        
        if contract_id:
            conflicting_contracts = conflicting_contracts.exclude(pk=contract_id)
        
        conflicts = []
        for contract in conflicting_contracts:
            if (hora_inicio < contract.hora_final and hora_final > contract.hora_inicio):
                conflicts.append({
                    'contract_id': contract.id,
                    'numero_contrato': contract.numero_contrato,
                    'titulo': contract.titulo,
                    'hora_inicio': contract.hora_inicio.strftime('%H:%M'),
                    'hora_final': contract.hora_final.strftime('%H:%M')
                })
        
        return Response({
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        })
