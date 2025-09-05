from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Repertorio, Generos


class RepertorioSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Repertorio"""
    
    duracion_formateada = serializers.ReadOnlyField()
    tiene_recursos = serializers.ReadOnlyField()
    etiquetas_lista = serializers.ReadOnlyField()
    popularidad = serializers.ReadOnlyField()
    dias_sin_tocar = serializers.ReadOnlyField()
    
    class Meta:
        model = Repertorio
        fields = [
            'id', 'is_active', 'created_at', 'updated_at', 'deleted_at',
            'nombre_cancion', 'artista', 'genero', 'duracion', 'duracion_segundos',
            'dificultad', 'tonalidad', 'tempo', 'link', 'link_partitura',
            'notas', 'veces_tocada', 'ultima_vez_tocada', 'etiquetas', 'es_favorita',
            # Campos calculados
            'duracion_formateada', 'tiene_recursos', 'etiquetas_lista', 
            'popularidad', 'dias_sin_tocar'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'deleted_at', 'duracion_segundos',
            'veces_tocada', 'ultima_vez_tocada', 'duracion_formateada', 
            'tiene_recursos', 'etiquetas_lista', 'popularidad', 'dias_sin_tocar'
        ]
    
    def validate_duracion(self, value):
        """Valida el formato de duración"""
        if value:
            import re
            patron = re.compile(r'^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$')
            if not patron.match(value.strip()):
                raise serializers.ValidationError(
                    'Formato inválido. Use MM:SS o HH:MM:SS'
                )
        return value
    
    def validate_tonalidad(self, value):
        """Valida el formato de tonalidad"""
        if value:
            import re
            patron = re.compile(r'^[A-G][#b]?[m]?$')
            if not patron.match(value.strip()):
                raise serializers.ValidationError(
                    'Formato inválido. Ejemplos: C, Am, F#, Bb'
                )
        return value
    
    def validate_tempo(self, value):
        """Valida el tempo"""
        if value is not None and (value < 40 or value > 300):
            raise serializers.ValidationError(
                'El tempo debe estar entre 40 y 300 BPM'
            )
        return value
    
    def validate(self, attrs):
        """Validaciones a nivel de objeto"""
        # Validar que no exista otra canción con el mismo nombre y artista
        nombre_cancion = attrs.get('nombre_cancion')
        artista = attrs.get('artista')
        
        if nombre_cancion and artista:
            queryset = Repertorio.objects.filter(
                nombre_cancion__iexact=nombre_cancion,
                artista__iexact=artista
            )
            
            # Si estamos actualizando, excluir el objeto actual
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    'Ya existe una canción con este nombre y artista'
                )
        
        return attrs


class RepertorioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de repertorio"""
    
    duracion_formateada = serializers.ReadOnlyField()
    popularidad = serializers.ReadOnlyField()
    
    class Meta:
        model = Repertorio
        fields = [
            'id', 'nombre_cancion', 'artista', 'genero', 'dificultad',
            'duracion_formateada', 'es_favorita', 'veces_tocada', 
            'popularidad', 'created_at'
        ]


class RepertorioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear canciones en el repertorio"""
    
    class Meta:
        model = Repertorio
        fields = [
            'nombre_cancion', 'artista', 'genero', 'duracion', 'dificultad',
            'tonalidad', 'tempo', 'link', 'link_partitura', 'notas', 
            'etiquetas', 'es_favorita'
        ]
    
    def validate_duracion(self, value):
        """Valida el formato de duración"""
        if value:
            import re
            patron = re.compile(r'^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$')
            if not patron.match(value.strip()):
                raise serializers.ValidationError(
                    'Formato inválido. Use MM:SS o HH:MM:SS'
                )
        return value
    
    def validate_tonalidad(self, value):
        """Valida el formato de tonalidad"""
        if value:
            import re
            patron = re.compile(r'^[A-G][#b]?[m]?$')
            if not patron.match(value.strip()):
                raise serializers.ValidationError(
                    'Formato inválido. Ejemplos: C, Am, F#, Bb'
                )
        return value
    
    def validate(self, attrs):
        """Validaciones a nivel de objeto"""
        # Validar que no exista otra canción con el mismo nombre y artista
        nombre_cancion = attrs.get('nombre_cancion')
        artista = attrs.get('artista')
        
        if nombre_cancion and artista:
            if Repertorio.objects.filter(
                nombre_cancion__iexact=nombre_cancion,
                artista__iexact=artista
            ).exists():
                raise serializers.ValidationError(
                    'Ya existe una canción con este nombre y artista'
                )
        
        return attrs


class RepertorioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar canciones del repertorio"""
    
    class Meta:
        model = Repertorio
        fields = [
            'nombre_cancion', 'artista', 'genero', 'duracion', 'dificultad',
            'tonalidad', 'tempo', 'link', 'link_partitura', 'notas', 
            'etiquetas', 'es_favorita'
        ]
    
    def validate_duracion(self, value):
        """Valida el formato de duración"""
        if value:
            import re
            patron = re.compile(r'^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$')
            if not patron.match(value.strip()):
                raise serializers.ValidationError(
                    'Formato inválido. Use MM:SS o HH:MM:SS'
                )
        return value
    
    def validate_tonalidad(self, value):
        """Valida el formato de tonalidad"""
        if value:
            import re
            patron = re.compile(r'^[A-G][#b]?[m]?$')
            if not patron.match(value.strip()):
                raise serializers.ValidationError(
                    'Formato inválido. Ejemplos: C, Am, F#, Bb'
                )
        return value
    
    def validate(self, attrs):
        """Validaciones a nivel de objeto"""
        # Validar que no exista otra canción con el mismo nombre y artista
        nombre_cancion = attrs.get('nombre_cancion')
        artista = attrs.get('artista')
        
        if nombre_cancion and artista:
            queryset = Repertorio.objects.filter(
                nombre_cancion__iexact=nombre_cancion,
                artista__iexact=artista
            )
            
            # Excluir el objeto actual de la validación
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    'Ya existe una canción con este nombre y artista'
                )
        
        return attrs


class RepertorioActionSerializer(serializers.Serializer):
    """Serializer para acciones sobre canciones del repertorio"""
    
    ACTION_CHOICES = [
        ('marcar_favorita', 'Marcar como favorita'),
        ('quitar_favorita', 'Quitar de favoritas'),
        ('marcar_tocada', 'Marcar como tocada'),
        ('agregar_etiqueta', 'Agregar etiqueta'),
        ('quitar_etiqueta', 'Quitar etiqueta'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    etiqueta = serializers.CharField(
        max_length=100, 
        required=False,
        help_text='Requerido para acciones de etiquetas'
    )
    
    def validate(self, attrs):
        action = attrs.get('action')
        etiqueta = attrs.get('etiqueta')
        
        # Validar que se proporcione etiqueta para acciones que la requieren
        if action in ['agregar_etiqueta', 'quitar_etiqueta'] and not etiqueta:
            raise serializers.ValidationError(
                'La etiqueta es requerida para esta acción'
            )
        
        return attrs


class RepertorioStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del repertorio"""
    
    total_canciones = serializers.IntegerField()
    total_artistas = serializers.IntegerField()
    total_generos = serializers.IntegerField()
    cancion_mas_tocada = serializers.CharField()
    artista_mas_frecuente = serializers.CharField()
    genero_mas_popular = serializers.CharField()
    duracion_total_segundos = serializers.IntegerField()
    duracion_total_formateada = serializers.CharField()
    canciones_favoritas = serializers.IntegerField()
    canciones_sin_tocar = serializers.IntegerField()
    promedio_veces_tocada = serializers.FloatField()
    
    # Distribución por género
    distribucion_generos = serializers.DictField()
    
    # Distribución por dificultad
    distribucion_dificultad = serializers.DictField()
    
    # Canciones recientes (últimos 30 días)
    canciones_recientes = serializers.IntegerField()
    
    # Top 10 canciones más tocadas
    top_canciones = RepertorioListSerializer(many=True)
    
    # Canciones favoritas
    canciones_favoritas_lista = RepertorioListSerializer(many=True)


class RepertorioSearchSerializer(serializers.Serializer):
    """Serializer para búsquedas en el repertorio"""
    
    search = serializers.CharField(
        required=False,
        help_text='Término de búsqueda en nombre de canción o artista'
    )
    genero = serializers.CharField(required=False)
    dificultad = serializers.CharField(required=False)
    artista = serializers.CharField(required=False)
    es_favorita = serializers.BooleanField(required=False)
    con_link = serializers.BooleanField(required=False)
    min_duracion = serializers.IntegerField(
        required=False,
        help_text='Duración mínima en segundos'
    )
    max_duracion = serializers.IntegerField(
        required=False,
        help_text='Duración máxima en segundos'
    )
    etiqueta = serializers.CharField(
        required=False,
        help_text='Filtrar por etiqueta específica'
    )
    
    def validate(self, attrs):
        min_dur = attrs.get('min_duracion')
        max_dur = attrs.get('max_duracion')
        
        if min_dur and max_dur and min_dur > max_dur:
            raise serializers.ValidationError(
                'La duración mínima no puede ser mayor que la máxima'
            )
        
        return attrs


class GenerosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generos
        fields = ['id', 'nombre', 'is_active', 'created_at', 'updated_at', 'deleted_at']