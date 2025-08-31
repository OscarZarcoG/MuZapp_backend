from django.db import models
from core.models import BaseModel, BaseModelManager
from django.utils import timezone

class MusicManager(BaseModelManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class AudioConversion(BaseModel):
    objects = MusicManager()
        
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('spotify', 'Spotify'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    # Información básica
    original_url = models.URLField(max_length=500, help_text="URL original del video/canción")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    title = models.CharField(max_length=200, blank=True, null=True)
    artist = models.CharField(max_length=200, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    
    
    # Archivo resultante
    audio_file = models.FileField(upload_to='converted_audio/', blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True, help_text="Tamaño del archivo en bytes")
    
    # Información adicional
    error_message = models.TextField(blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Conversión de Audio'
        verbose_name_plural = 'Conversiones de Audio'
    
    def __str__(self):
        return f"{self.title or 'Sin título'} - {self.get_platform_display()}"
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
