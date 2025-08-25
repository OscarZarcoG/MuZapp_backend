# GIGS/AUDIO/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import AudioEquipment

class AudioEquipmentSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    esta_disponible = serializers.ReadOnlyField()
    necesita_mantenimiento = serializers.ReadOnlyField()
    
    class Meta:
        model = AudioEquipment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    
    def validate_precio_compra(self, value):
        """Validar que el precio de compra sea positivo"""
        if value is not None and value < 0:
            raise serializers.ValidationError("El precio de compra no puede ser negativo.")
        return value
    
    def validate_fecha_compra(self, value):
        """Validar que la fecha de compra no sea futura"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("La fecha de compra no puede ser futura.")
        return value
    
    def validate_garantia_hasta(self, value):
        """Validar que la fecha de garantía sea posterior a la fecha de compra"""
        if value and self.initial_data.get('fecha_compra'):
            fecha_compra = self.initial_data.get('fecha_compra')
            if isinstance(fecha_compra, str):
                from datetime import datetime
                fecha_compra = datetime.strptime(fecha_compra, '%Y-%m-%d').date()
            if value <= fecha_compra:
                raise serializers.ValidationError(
                    "La fecha de garantía debe ser posterior a la fecha de compra."
                )
        return value
    
    def validate_numero_serie(self, value):
        """Validar que el número de serie sea único"""
        if value:
            # Verificar si ya existe otro equipo con el mismo número de serie
            queryset = AudioEquipment.objects.filter(numero_serie=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe un equipo con este número de serie."
                )
        return value
    
    def validate(self, attrs):
        """Validaciones generales"""
        # Validar que si el estado es 'vendido', no se pueda cambiar a otro estado
        if self.instance and self.instance.estado == 'vendido':
            if attrs.get('estado') and attrs.get('estado') != 'vendido':
                raise serializers.ValidationError(
                    "No se puede cambiar el estado de un equipo vendido."
                )
        
        # Validar que si el equipo está en uso, tenga una ubicación
        if attrs.get('estado') == 'en_uso' and not attrs.get('ubicacion'):
            if not (self.instance and self.instance.ubicacion):
                raise serializers.ValidationError(
                    "Un equipo en uso debe tener una ubicación especificada."
                )
        
        return attrs