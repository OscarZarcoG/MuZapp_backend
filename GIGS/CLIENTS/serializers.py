from rest_framework import serializers
from .models import Client
from core.exceptions import ValidationError

class ClientSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    es_empresa = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at', 'nombre_completo', 'es_empresa')
    
    def validate_email(self, value):
        """Validar formato de email si se proporciona"""
        if value and not value.strip():
            return None
        return value
    
    def validate_telefono(self, value):
        """Validar que el teléfono no esté vacío"""
        if not value or not value.strip():
            raise ValidationError("El teléfono es obligatorio")
        return value
    
    def validate(self, data):
        """Validaciones generales del cliente"""
        # Si es empresa u organización, validar que tenga nombre de empresa
        if data.get('tipo_cliente') in ['empresa', 'organizacion']:
            if not data.get('empresa'):
                raise ValidationError({
                    'empresa': 'El nombre de la empresa es obligatorio para este tipo de cliente'
                })
        
        return data