from rest_framework import serializers
from .models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class EquipoAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_Audio
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class CateringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catering
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class PeticionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peticion
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class RepertorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repertorio
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class FotosEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fotos_Evento
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class ContratoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_cliente', read_only=True)
    equipo_audio_nombre = serializers.CharField(source='equipo_audio.__str__', read_only=True)
    catering_descripcion = serializers.CharField(source='catering.peticion_grupo', read_only=True)
    peticiones_cliente_nombres = serializers.StringRelatedField(source='peticiones_cliente', many=True, read_only=True)
    
    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'deleted_at', 
            'numero_contrato', 'tiempo_total', 'pago_total', 
            'pago_restante', 'porcentaje', 'cliente_nombre',
            'equipo_audio_nombre', 'catering_descripcion',
            'peticiones_cliente_nombres'
        )
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data.get('hora_final') and data.get('hora_inicio'):
            if data['hora_final'] == data['hora_inicio']:
                raise serializers.ValidationError(
                    "La hora de finalización debe ser diferente a la hora de inicio"
                )
        
        if data.get('pago_adelanto', 0) < 0:
            raise serializers.ValidationError(
                "El adelanto no puede ser negativo"
            )
        
        if data.get('costo_hora', 0) < 0:
            raise serializers.ValidationError(
                "El costo por hora no puede ser negativo"
            )
        
        return data


class ContratoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear contratos con validaciones adicionales"""
    
    class Meta:
        model = Contrato
        exclude = (
            'numero_contrato', 'tiempo_total', 'pago_total', 
            'pago_restante', 'porcentaje', 'created_at', 
            'updated_at', 'deleted_at'
        )
    
    def create(self, validated_data):
        """Crear contrato con cálculos automáticos"""
        peticiones = validated_data.pop('peticiones_cliente', [])
        contrato = Contrato.objects.create(**validated_data)
        
        if peticiones:
            contrato.peticiones_cliente.set(peticiones)
        
        return contrato


class ContratoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de contratos"""
    cliente_nombre = serializers.CharField(source='cliente.nombre_cliente', read_only=True)
    estado_evento_display = serializers.CharField(source='get_estado_evento_display', read_only=True)
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    
    class Meta:
        model = Contrato
        fields = (
            'id', 'numero_contrato', 'titulo', 'tipo_evento', 
            'tipo_evento_display', 'estado_evento', 'estado_evento_display',
            'fecha_evento', 'hora_inicio', 'hora_final', 
            'cliente_nombre', 'pago_total', 'porcentaje'
        )