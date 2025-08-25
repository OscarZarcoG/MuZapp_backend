from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from .models import EventPhoto
from ..CLIENTS.serializers import ClientSerializer
from ..CONTRACT.serializers import ContractListSerializer


class EventPhotoSerializer(serializers.ModelSerializer):
    """Serializer completo para EventPhoto"""
    
    # Campos calculados de solo lectura
    tamaño_archivo_mb = serializers.ReadOnlyField()
    resolucion = serializers.ReadOnlyField()
    es_horizontal = serializers.ReadOnlyField()
    es_cuadrada = serializers.ReadOnlyField()
    dias_desde_evento = serializers.ReadOnlyField()
    url_foto = serializers.ReadOnlyField()
    
    # Información de relaciones
    cliente_info = ClientSerializer(source='cliente', read_only=True)
    contrato_info = ContractListSerializer(source='contrato', read_only=True)
    
    # Campos adicionales
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    
    class Meta:
        model = EventPhoto
        fields = [
            'id', 'nombre_foto', 'foto', 'fecha_foto', 'evento', 'fecha_evento',
            'tipo_evento', 'tipo_evento_display', 'ubicacion', 'descripcion',
            'fotografo', 'publicas', 'destacadas', 'cliente', 'contrato',
            'ancho_imagen', 'alto_imagen', 'tamaño_archivo', 'tamaño_archivo_mb',
            'resolucion', 'es_horizontal', 'es_cuadrada', 'dias_desde_evento',
            'url_foto', 'cliente_info', 'contrato_info', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'ancho_imagen', 'alto_imagen', 'tamaño_archivo',
            'created_at', 'updated_at'
        ]
    
    def validate_fecha_foto(self, value):
        """Validar fecha de la foto"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de la foto no puede ser futura."
            )
        return value
    
    def validate_fecha_evento(self, value):
        """Validar fecha del evento"""
        from datetime import timedelta
        
        # No puede ser muy antigua (más de 10 años)
        limite_antiguo = timezone.now().date() - timedelta(days=365*10)
        if value < limite_antiguo:
            raise serializers.ValidationError(
                "La fecha del evento no puede ser anterior a 10 años."
            )
        
        return value
    
    def validate_evento(self, value):
        """Validar nombre del evento"""
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre del evento debe tener al menos 3 caracteres."
            )
        return value.strip() if value else value
    
    def validate_foto(self, value):
        """Validar archivo de foto"""
        if value:
            # Validar tamaño máximo (10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    "El archivo no puede ser mayor a 10MB."
                )
            
            # Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Solo se permiten archivos JPG, PNG o WEBP."
                )
        
        return value
    
    def validate(self, attrs):
        """Validaciones cruzadas"""
        fecha_foto = attrs.get('fecha_foto')
        fecha_evento = attrs.get('fecha_evento')
        
        # Validar que fecha_foto no sea anterior a fecha_evento (con margen de 1 día)
        if fecha_foto and fecha_evento:
            from datetime import timedelta
            if fecha_foto < fecha_evento - timedelta(days=1):
                raise serializers.ValidationError({
                    'fecha_foto': 'La fecha de la foto no puede ser anterior al evento.'
                })
        
        return attrs


class EventPhotoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de fotos"""
    
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    url_foto = serializers.ReadOnlyField()
    tamaño_archivo_mb = serializers.ReadOnlyField()
    resolucion = serializers.ReadOnlyField()
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    
    class Meta:
        model = EventPhoto
        fields = [
            'id', 'nombre_foto', 'url_foto', 'fecha_foto', 'evento',
            'fecha_evento', 'tipo_evento', 'tipo_evento_display', 'ubicacion',
            'fotografo', 'publicas', 'destacadas', 'tamaño_archivo_mb',
            'resolucion', 'cliente_nombre'
        ]


class EventPhotoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear fotos de eventos"""
    
    class Meta:
        model = EventPhoto
        fields = [
            'nombre_foto', 'foto', 'fecha_foto', 'evento', 'fecha_evento',
            'tipo_evento', 'ubicacion', 'descripcion', 'fotografo',
            'publicas', 'destacadas', 'cliente', 'contrato'
        ]
    
    def validate_fecha_foto(self, value):
        """Validar fecha de la foto"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de la foto no puede ser futura."
            )
        return value
    
    def validate_fecha_evento(self, value):
        """Validar fecha del evento"""
        from datetime import timedelta
        
        limite_antiguo = timezone.now().date() - timedelta(days=365*10)
        if value < limite_antiguo:
            raise serializers.ValidationError(
                "La fecha del evento no puede ser anterior a 10 años."
            )
        
        return value
    
    def validate_evento(self, value):
        """Validar nombre del evento"""
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre del evento debe tener al menos 3 caracteres."
            )
        return value.strip() if value else value
    
    def validate_foto(self, value):
        """Validar archivo de foto"""
        if value:
            # Validar tamaño máximo (10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    "El archivo no puede ser mayor a 10MB."
                )
            
            # Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Solo se permiten archivos JPG, PNG o WEBP."
                )
        
        return value
    
    def validate(self, attrs):
        """Validaciones cruzadas"""
        fecha_foto = attrs.get('fecha_foto')
        fecha_evento = attrs.get('fecha_evento')
        
        if fecha_foto and fecha_evento:
            from datetime import timedelta
            if fecha_foto < fecha_evento - timedelta(days=1):
                raise serializers.ValidationError({
                    'fecha_foto': 'La fecha de la foto no puede ser anterior al evento.'
                })
        
        return attrs


class EventPhotoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar fotos de eventos"""
    
    class Meta:
        model = EventPhoto
        fields = [
            'nombre_foto', 'fecha_foto', 'evento', 'fecha_evento',
            'tipo_evento', 'ubicacion', 'descripcion', 'fotografo',
            'publicas', 'destacadas', 'cliente', 'contrato'
        ]
    
    def validate_fecha_foto(self, value):
        """Validar fecha de la foto"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de la foto no puede ser futura."
            )
        return value
    
    def validate_fecha_evento(self, value):
        """Validar fecha del evento"""
        from datetime import timedelta
        
        limite_antiguo = timezone.now().date() - timedelta(days=365*10)
        if value < limite_antiguo:
            raise serializers.ValidationError(
                "La fecha del evento no puede ser anterior a 10 años."
            )
        
        return value
    
    def validate_evento(self, value):
        """Validar nombre del evento"""
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre del evento debe tener al menos 3 caracteres."
            )
        return value.strip() if value else value


class EventPhotoActionSerializer(serializers.Serializer):
    """Serializer para acciones sobre fotos"""
    
    accion = serializers.ChoiceField(
        choices=[
            ('destacar', 'Marcar como destacada'),
            ('quitar_destacada', 'Quitar de destacadas'),
            ('hacer_publica', 'Hacer pública'),
            ('hacer_privada', 'Hacer privada'),
        ],
        help_text="Acción a realizar sobre la foto"
    )
    
    def validate_accion(self, value):
        """Validar acción"""
        if not value:
            raise serializers.ValidationError("Debe especificar una acción.")
        return value


class EventPhotoStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de fotos"""
    
    total_fotos = serializers.IntegerField(read_only=True)
    fotos_publicas = serializers.IntegerField(read_only=True)
    fotos_destacadas = serializers.IntegerField(read_only=True)
    fotos_privadas = serializers.IntegerField(read_only=True)
    eventos_con_fotos = serializers.IntegerField(read_only=True)
    fotografos_activos = serializers.IntegerField(read_only=True)
    tamaño_total_mb = serializers.FloatField(read_only=True)
    
    # Estadísticas por tipo de evento
    por_tipo_evento = serializers.DictField(read_only=True)
    
    # Estadísticas mensuales
    por_mes = serializers.ListField(read_only=True)
    
    # Top fotógrafos
    top_fotografos = serializers.ListField(read_only=True)