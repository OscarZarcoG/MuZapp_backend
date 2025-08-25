# GIGS/CATERING/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Catering

class CateringSerializer(serializers.ModelSerializer):
    esta_pendiente = serializers.ReadOnlyField()
    esta_confirmado = serializers.ReadOnlyField()
    puede_cancelar = serializers.ReadOnlyField()
    
    class Meta:
        model = Catering
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    
    def validate_presupuesto_estimado(self, value):
        """Validar que el presupuesto estimado sea positivo"""
        if value is not None and value < 0:
            raise serializers.ValidationError("El presupuesto estimado no puede ser negativo.")
        return value
    
    def validate_numero_personas(self, value):
        """Validar que el número de personas sea positivo"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("El número de personas debe ser mayor a cero.")
        return value
    
    def validate_fecha_evento(self, value):
        """Validar que la fecha del evento no sea pasada"""
        if value and value < timezone.now():
            raise serializers.ValidationError("La fecha del evento no puede ser en el pasado.")
        return value
    
    def validate(self, attrs):
        """Validaciones generales"""
        # Validar que si el estado es 'confirmado', debe tener proveedor
        if attrs.get('estado') == 'confirmado':
            if not attrs.get('proveedor') and not (self.instance and self.instance.proveedor):
                raise serializers.ValidationError(
                    "Para confirmar el catering debe especificar un proveedor."
                )
        
        # Validar que si el estado es 'completado', debe haber estado confirmado antes
        if attrs.get('estado') == 'completado':
            if self.instance and self.instance.estado not in ['confirmado']:
                raise serializers.ValidationError(
                    "Solo se puede completar un catering que esté confirmado."
                )
        
        # Validar que no se pueda cambiar de 'cancelado' a otro estado
        if self.instance and self.instance.estado == 'cancelado':
            if attrs.get('estado') and attrs.get('estado') != 'cancelado':
                raise serializers.ValidationError(
                    "No se puede cambiar el estado de un catering cancelado."
                )
        
        # Validar que no se pueda cambiar de 'completado' a otro estado
        if self.instance and self.instance.estado == 'completado':
            if attrs.get('estado') and attrs.get('estado') != 'completado':
                raise serializers.ValidationError(
                    "No se puede cambiar el estado de un catering completado."
                )
        
        return attrs