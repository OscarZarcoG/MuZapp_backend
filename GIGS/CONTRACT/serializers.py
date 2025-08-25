from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal
from datetime import datetime, time
from .models import Contract
from ..CLIENTS.models import Client
from ..CLIENTS.serializers import ClientSerializer


class ContractSerializer(serializers.ModelSerializer):
    """Serializer completo para Contract"""
    
    # Campos de solo lectura calculados
    tiempo_total_display = serializers.SerializerMethodField()
    duracion_horas = serializers.ReadOnlyField()
    dias_hasta_evento = serializers.SerializerMethodField()
    pago_restante = serializers.ReadOnlyField()
    porcentaje = serializers.ReadOnlyField()
    porcentaje_adelanto = serializers.SerializerMethodField()
    costo_por_persona = serializers.SerializerMethodField()
    esta_proximo = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()
    
    # Información del cliente (solo lectura)
    cliente_info = ClientSerializer(source='cliente', read_only=True)
    cliente_nombre_completo = serializers.SerializerMethodField()
    
    # Información de relaciones (solo lectura)
    equipo_audio_nombre = serializers.CharField(source='equipo_audio.nombre', read_only=True)
    catering_nombre = serializers.CharField(source='catering.nombre', read_only=True)
    total_peticiones = serializers.SerializerMethodField()
    
    # Estado del contrato
    estado_evento_display = serializers.CharField(source='get_estado_evento_display', read_only=True)
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    
    # Campos de validación
    numero_contrato = serializers.CharField(read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id', 'numero_contrato', 'estado_evento', 'estado_evento_display',
            'titulo', 'tipo_evento', 'tipo_evento_display', 'nombre_festejado', 'notas',
            'fecha_evento', 'hora_inicio', 'hora_final', 'tiempo_total', 'tiempo_total_display',
            'duracion_horas', 'dias_hasta_evento',
            'oportunidades_descanso', 'tiempo_descanso', 'descripcion_descanso',
            'nombre_lugar', 'descripcion_lugar', 'google_maps_url', 'fotos_lugar',
            'pago_total', 'costo_hora', 'pago_adelanto', 'pago_restante', 'porcentaje',
            'porcentaje_adelanto', 'costo_extra', 'costo_por_persona',
            'cliente', 'cliente_info', 'cliente_nombre_completo', 'audiencia',
            'equipo_audio', 'equipo_audio_nombre', 'catering', 'catering_nombre',
            'peticiones_cliente', 'total_peticiones',
            'esta_proximo', 'esta_vencido',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'numero_contrato', 'tiempo_total', 'pago_restante', 'porcentaje',
            'duracion_horas', 'esta_proximo', 'esta_vencido',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def get_tiempo_total_display(self, obj):
        """Formato legible del tiempo total"""
        if obj.tiempo_total:
            horas = obj.tiempo_total // 60
            minutos = obj.tiempo_total % 60
            if horas > 0 and minutos > 0:
                return f"{horas}h {minutos}m"
            elif horas > 0:
                return f"{horas}h"
            else:
                return f"{minutos}m"
        return None
    
    def get_dias_hasta_evento(self, obj):
        """Días hasta el evento"""
        return obj.dias_hasta_evento()
    
    def get_porcentaje_adelanto(self, obj):
        """Porcentaje del adelanto"""
        return obj.porcentaje_adelanto()
    
    def get_costo_por_persona(self, obj):
        """Costo por persona"""
        return obj.costo_por_persona()
    
    def get_cliente_nombre_completo(self, obj):
        """Nombre completo del cliente"""
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellidos}".strip()
        return None
    
    def get_total_peticiones(self, obj):
        """Total de peticiones del cliente"""
        return obj.peticiones_cliente.count()
    
    def validate_fecha_evento(self, value):
        """Validar fecha del evento"""
        from django.utils import timezone
        
        # Solo validar para nuevos contratos
        if not self.instance and value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha del evento no puede ser en el pasado."
            )
        return value
    
    def validate_pago_adelanto(self, value):
        """Validar que el adelanto no sea mayor al total"""
        pago_total = self.initial_data.get('pago_total')
        if pago_total and value > Decimal(str(pago_total)):
            raise serializers.ValidationError(
                "El adelanto no puede ser mayor al pago total."
            )
        return value
    
    def validate_hora_final(self, value):
        """Validar que la hora final sea posterior a la inicial"""
        hora_inicio = self.initial_data.get('hora_inicio')
        if hora_inicio:
            if isinstance(hora_inicio, str):
                try:
                    hora_inicio = datetime.strptime(hora_inicio, '%H:%M:%S').time()
                except ValueError:
                    try:
                        hora_inicio = datetime.strptime(hora_inicio, '%H:%M').time()
                    except ValueError:
                        pass
            
            if isinstance(hora_inicio, time) and value <= hora_inicio:
                # Permitir si es al día siguiente (diferencia mayor a 12 horas)
                inicio_minutes = hora_inicio.hour * 60 + hora_inicio.minute
                final_minutes = value.hour * 60 + value.minute
                
                if final_minutes + (24 * 60) - inicio_minutes < 60:  # Menos de 1 hora
                    raise serializers.ValidationError(
                        "La hora final debe ser posterior a la hora de inicio."
                    )
        return value
    
    def validate_audiencia(self, value):
        """Validar audiencia"""
        if value < 1:
            raise serializers.ValidationError(
                "La audiencia debe ser al menos 1 persona."
            )
        return value
    
    def validate_tiempo_descanso(self, value):
        """Validar tiempo de descanso"""
        if value is not None and value > 120:
            raise serializers.ValidationError(
                "El tiempo de descanso no puede ser mayor a 120 minutos."
            )
        return value
    
    def validate_oportunidades_descanso(self, value):
        """Validar oportunidades de descanso"""
        if value is not None and value > 10:
            raise serializers.ValidationError(
                "No se pueden programar más de 10 descansos."
            )
        return value
    
    def validate(self, attrs):
        """Validaciones generales"""
        # Validar conflictos de horario si se proporcionan los datos necesarios
        fecha_evento = attrs.get('fecha_evento')
        hora_inicio = attrs.get('hora_inicio')
        hora_final = attrs.get('hora_final')
        
        if fecha_evento and hora_inicio and hora_final:
            # Crear una instancia temporal para validar conflictos
            temp_contract = Contract(
                fecha_evento=fecha_evento,
                hora_inicio=hora_inicio,
                hora_final=hora_final
            )
            if self.instance:
                temp_contract.pk = self.instance.pk
            
            try:
                temp_contract.validate_schedule_conflict()
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        
        return attrs


class ContractListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de contratos"""
    
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_apellidos = serializers.CharField(source='cliente.apellidos', read_only=True)
    estado_evento_display = serializers.CharField(source='get_estado_evento_display', read_only=True)
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    dias_hasta_evento = serializers.SerializerMethodField()
    duracion_horas = serializers.ReadOnlyField()
    esta_proximo = serializers.ReadOnlyField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'numero_contrato', 'titulo', 'estado_evento', 'estado_evento_display',
            'tipo_evento', 'tipo_evento_display', 'fecha_evento', 'hora_inicio', 'hora_final',
            'nombre_lugar', 'pago_total', 'pago_adelanto', 'pago_restante',
            'cliente', 'cliente_nombre', 'cliente_apellidos', 'audiencia',
            'dias_hasta_evento', 'duracion_horas', 'esta_proximo',
            'created_at', 'updated_at'
        ]
    
    def get_dias_hasta_evento(self, obj):
        """Días hasta el evento"""
        return obj.dias_hasta_evento()


class ContractActionSerializer(serializers.Serializer):
    """Serializer para acciones sobre contratos"""
    
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notas adicionales para la acción"
    )
    motivo_cancelacion = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Motivo de cancelación (requerido para cancelar)"
    )
    
    def validate_motivo_cancelacion(self, value):
        """Validar motivo de cancelación"""
        action = self.context.get('action')
        if action == 'cancelar' and not value:
            raise serializers.ValidationError(
                "El motivo de cancelación es requerido."
            )
        return value


class ContractCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear contratos (campos mínimos requeridos)"""
    
    class Meta:
        model = Contract
        fields = [
            'titulo', 'tipo_evento', 'nombre_festejado', 'notas',
            'fecha_evento', 'hora_inicio', 'hora_final',
            'oportunidades_descanso', 'tiempo_descanso', 'descripcion_descanso',
            'nombre_lugar', 'descripcion_lugar', 'google_maps_url',
            'pago_total', 'costo_hora', 'pago_adelanto', 'costo_extra',
            'cliente', 'audiencia', 'equipo_audio', 'catering'
        ]
    
    def validate_fecha_evento(self, value):
        """Validar fecha del evento"""
        from django.utils import timezone
        
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha del evento no puede ser en el pasado."
            )
        return value
    
    def validate_pago_adelanto(self, value):
        """Validar que el adelanto no sea mayor al total"""
        pago_total = self.initial_data.get('pago_total')
        if pago_total and value > Decimal(str(pago_total)):
            raise serializers.ValidationError(
                "El adelanto no puede ser mayor al pago total."
            )
        return value


class ContractUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar contratos"""
    
    class Meta:
        model = Contract
        fields = [
            'titulo', 'tipo_evento', 'nombre_festejado', 'notas',
            'fecha_evento', 'hora_inicio', 'hora_final',
            'oportunidades_descanso', 'tiempo_descanso', 'descripcion_descanso',
            'nombre_lugar', 'descripcion_lugar', 'google_maps_url',
            'pago_total', 'costo_hora', 'pago_adelanto', 'costo_extra',
            'audiencia', 'equipo_audio', 'catering', 'peticiones_cliente'
        ]
    
    def validate_pago_adelanto(self, value):
        """Validar que el adelanto no sea mayor al total"""
        pago_total = self.initial_data.get('pago_total', self.instance.pago_total)
        if pago_total and value > pago_total:
            raise serializers.ValidationError(
                "El adelanto no puede ser mayor al pago total."
            )
        return value
    
    def validate(self, attrs):
        """Validaciones generales para actualización"""
        # No permitir cambiar cliente en contratos confirmados o en progreso
        if self.instance and self.instance.estado_evento in ['confirmed', 'in_progress']:
            if 'cliente' in attrs and attrs['cliente'] != self.instance.cliente:
                raise serializers.ValidationError({
                    'cliente': 'No se puede cambiar el cliente en un contrato confirmado o en progreso.'
                })
        
        return attrs