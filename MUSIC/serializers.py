from rest_framework import serializers
from .models import AudioConversion


class AudioConversionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo AudioConversion"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = AudioConversion
        fields = [
            'id', 'original_url', 'platform', 'title', 'artist', 'duration',
            'audio_file', 'file_size', 'file_size_mb', 'error_message', 
            'download_count', 'is_completed'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_active', 'title', 'artist',
            'duration', 'audio_file', 'file_size', 'error_message', 'download_count'
        ]


class ConvertAudioSerializer(serializers.Serializer):
    """Serializer para la conversión de audio"""
    
    url = serializers.URLField(
        help_text="URL de YouTube o Spotify para convertir a MP3"
    )
    
    def validate_url(self, value):
        """Validar que la URL sea de YouTube o Spotify"""
        youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
        spotify_domains = ['spotify.com', 'open.spotify.com']
        
        is_youtube = any(domain in value.lower() for domain in youtube_domains)
        is_spotify = any(domain in value.lower() for domain in spotify_domains)
        
        if not (is_youtube or is_spotify):
            raise serializers.ValidationError(
                "La URL debe ser de YouTube o Spotify"
            )
        
        return value


class AudioConversionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar conversiones"""
    
    file_size_mb = serializers.ReadOnlyField()
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AudioConversion
        fields = [
            'id', 'title', 'artist', 'platform', 'platform_display',
            'is_active', 'status', 'status_display', 'created_at', 'file_size_mb', 'download_count'
        ]