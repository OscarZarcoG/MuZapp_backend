from rest_framework import serializers
from .models import Pais, Estado, Municipio, Colonia


class PaisSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Pais"""
    total_estados = serializers.SerializerMethodField()
    
    class Meta:
        model = Pais
        fields = ['id', 'nombre', 'total_estados']
    
    def get_total_estados(self, obj):
        return obj.estados.count()


class EstadoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Estado"""
    pais_nombre = serializers.CharField(source='pais.nombre', read_only=True)
    total_municipios = serializers.SerializerMethodField()
    
    class Meta:
        model = Estado
        fields = ['id', 'nombre', 'pais', 'pais_nombre', 'total_municipios']
    
    def get_total_municipios(self, obj):
        return obj.municipios.count()


class MunicipioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Municipio"""
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    pais_nombre = serializers.CharField(source='estado.pais.nombre', read_only=True)
    total_colonias = serializers.SerializerMethodField()
    
    class Meta:
        model = Municipio
        fields = ['id', 'nombre', 'estado', 'estado_nombre', 'pais_nombre', 'total_colonias']
    
    def get_total_colonias(self, obj):
        return obj.colonias.count()


class ColoniaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Colonia"""
    municipio_nombre = serializers.CharField(source='municipio.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='municipio.estado.nombre', read_only=True)
    pais_nombre = serializers.CharField(source='municipio.estado.pais.nombre', read_only=True)
    
    class Meta:
        model = Colonia
        fields = [
            'id', 'nombre', 'ciudad', 'municipio', 'asentamiento', 'codigo_postal',
            'municipio_nombre', 'estado_nombre', 'pais_nombre'
        ]


class ColoniaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para el modelo Colonia con información completa"""
    municipio = MunicipioSerializer(read_only=True)
    
    class Meta:
        model = Colonia
        fields = [
            'id', 'nombre', 'ciudad', 'municipio', 'asentamiento', 'codigo_postal'
        ]


class EstadoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para el modelo Estado con municipios"""
    pais = PaisSerializer(read_only=True)
    municipios = MunicipioSerializer(many=True, read_only=True)
    
    class Meta:
        model = Estado
        fields = ['id', 'nombre', 'pais', 'municipios']


class PaisDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para el modelo Pais con estados"""
    estados = EstadoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pais
        fields = ['id', 'nombre', 'estados']