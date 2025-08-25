from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import date
from .models import ClientRequest


class ClientRequestSerializer(serializers.ModelSerializer):
    """Serializer para ClientRequest"""
    
    # Campos de solo lectura calculados
    nombre_completo_cancion = serializers.ReadOnlyField()
    esta_pendiente = serializers.ReadOnlyField()
    esta_aprobada = serializers.ReadOnlyField()
    esta_rechazada = serializers.ReadOnlyField()
    es_urgente = serializers.ReadOnlyField()
    dias_hasta_fecha_necesaria = serializers.ReadOnlyField()
    
    # Información del cliente (solo lectura)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    cliente_telefono = serializers.CharField(source='cliente.telefono', read_only=True)
    cliente_email = serializers.CharField(source='cliente.email', read_only=True)
    
    # Información del evento (solo lectura)
    evento_titulo = serializers.CharField(source='evento_relacionado.titulo', read_only=True)
    evento_fecha = serializers.DateField(source='evento_relacionado.fecha_evento', read_only=True)
    
    class Meta:
        model = ClientRequest
        fields = [
            'id',
            'nombre_cancion',
            'artista',
            'album',
            'genero',
            'link',
            'link_partitura',
            'cliente',
            'cliente_nombre',
            'cliente_telefono',
            'cliente_email',
            'evento_relacionado',
            'evento_titulo',
            'evento_fecha',
            'estado',
            'prioridad',
            'fecha_solicitud',
            'fecha_necesaria',
            'fecha_respuesta',
            'notas_cliente',
            'notas_internas',
            'motivo_rechazo',
            'dificultad_estimada',
            'tiempo_estimado_aprendizaje',
            'nombre_completo_cancion',
            'esta_pendiente',
            'esta_aprobada',
            'esta_rechazada',
            'es_urgente',
            'dias_hasta_fecha_necesaria',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'fecha_solicitud',
            'fecha_respuesta',
            'created_at',
            'updated_at',
        ]
    
    def validate_fecha_necesaria(self, value):
        """Valida que la fecha necesaria no sea en el pasado"""
        if value and value < date.today():
            raise serializers.ValidationError(
                "La fecha necesaria no puede ser anterior a hoy."
            )
        return value
    
    def validate_tiempo_estimado_aprendizaje(self, value):
        """Valida que el tiempo estimado sea positivo"""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El tiempo estimado debe ser mayor a 0 horas."
            )
        return value
    
    def validate_link(self, value):
        """Valida que el enlace sea válido"""
        if value and not any(domain in value.lower() for domain in ['youtube.com', 'youtu.be', 'spotify.com', 'soundcloud.com', 'apple.com']):
            # Solo advertencia, no error
            pass
        return value
    
    def validate(self, attrs):
        """Validaciones generales"""
        # Validar que si está rechazada, tenga motivo
        if attrs.get('estado') == 'rechazada' and not attrs.get('motivo_rechazo'):
            raise serializers.ValidationError({
                'motivo_rechazo': 'Debe especificar un motivo para rechazar la petición.'
            })
        
        # No permitir cambiar estado a rechazada sin motivo
        if self.instance and attrs.get('estado') == 'rechazada':
            if not attrs.get('motivo_rechazo') and not self.instance.motivo_rechazo:
                raise serializers.ValidationError({
                    'motivo_rechazo': 'Debe especificar un motivo para rechazar la petición.'
                })
        
        # Validar que no se pueda cambiar de rechazada/en_repertorio a pendiente
        if self.instance and self.instance.estado in ['rechazada', 'en_repertorio']:
            if attrs.get('estado') == 'pendiente':
                raise serializers.ValidationError({
                    'estado': f'No se puede cambiar de {self.instance.get_estado_display()} a Pendiente.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Crear nueva petición"""
        # Asegurar que las nuevas peticiones empiecen como pendientes
        validated_data['estado'] = 'pendiente'
        return super().create(validated_data)


class ClientRequestListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    evento_titulo = serializers.CharField(source='evento_relacionado.titulo', read_only=True)
    nombre_completo_cancion = serializers.ReadOnlyField()
    esta_pendiente = serializers.ReadOnlyField()
    es_urgente = serializers.ReadOnlyField()
    dias_hasta_fecha_necesaria = serializers.ReadOnlyField()
    
    class Meta:
        model = ClientRequest
        fields = [
            'id',
            'nombre_cancion',
            'artista',
            'cliente_nombre',
            'evento_titulo',
            'estado',
            'prioridad',
            'fecha_solicitud',
            'fecha_necesaria',
            'nombre_completo_cancion',
            'esta_pendiente',
            'es_urgente',
            'dias_hasta_fecha_necesaria',
        ]


class ClientRequestActionSerializer(serializers.Serializer):
    """Serializer para acciones sobre peticiones"""
    
    notas_internas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notas internas para la acción"
    )
    motivo_rechazo = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Motivo de rechazo (requerido para rechazar)"
    )
    
    def validate_motivo_rechazo(self, value):
        """Valida que el motivo de rechazo no esté vacío cuando se requiere"""
        action = self.context.get('action')
        if action == 'reject' and not value:
            raise serializers.ValidationError(
                "El motivo de rechazo es requerido para rechazar una petición."
            )
        return value