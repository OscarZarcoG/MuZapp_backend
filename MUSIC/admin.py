from django.contrib import admin
from .models import AudioConversion

@admin.register(AudioConversion)
class AudioConversionAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'platform', 'status', 'created_at', 'download_count')
    list_filter = ('platform', 'status', 'created_at')
    search_fields = ('title', 'artist', 'original_url')
    readonly_fields = ('created_at', 'updated_at', 'file_size')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('title', 'artist', 'platform', 'original_url')
        }),
        ('Estado y archivos', {
            'fields': ('status', 'audio_file', 'file_size', 'duration')
        }),
        ('Estadísticas', {
            'fields': ('download_count', 'created_at', 'updated_at')
        }),
        ('Errores', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
