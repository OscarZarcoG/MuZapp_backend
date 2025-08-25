from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import Repertorio


@admin.register(Repertorio)
class RepertorioAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Repertorio"""
    
    list_display = [
        'nombre_cancion', 'artista', 'genero_badge', 'duracion_formateada',
        'dificultad_badge', 'veces_tocada', 'favorita_badge', 
        'tiene_recursos_badge', 'created_at'
    ]
    
    list_filter = [
        'genero', 'dificultad', 'es_favorita', 'tonalidad',
        'created_at', 'ultima_vez_tocada', 'veces_tocada'
    ]
    
    search_fields = [
        'nombre_cancion', 'artista', 'genero', 'etiquetas', 'notas'
    ]
    
    readonly_fields = [
        'id', 'duracion_segundos', 'duracion_formateada', 'tiene_recursos',
        'etiquetas_lista', 'popularidad', 'dias_sin_tocar', 'created_at', 
        'updated_at', 'deleted_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_cancion', 'artista', 'genero')
        }),
        ('Detalles Musicales', {
            'fields': ('dificultad', 'tonalidad', 'tempo', 'duracion', 'duracion_segundos')
        }),
        ('Enlaces y Recursos', {
            'fields': ('link', 'link_partitura'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('notas', 'etiquetas'),
            'classes': ('collapse',)
        }),
        ('Estadísticas de Uso', {
            'fields': ('veces_tocada', 'ultima_vez_tocada', 'es_favorita'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at', 'is_active'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['nombre_cancion', 'artista']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    actions = [
        'mark_as_favorite', 'remove_favorite', 'mark_as_played',
        'reset_play_count', 'restore_songs'
    ]
    
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo datos relacionados"""
        return super().get_queryset(request).select_related()
    
    def genero_badge(self, obj):
        """Muestra el género como badge colorido"""
        colors = {
            'Rock': '#e74c3c',
            'Pop': '#3498db', 
            'Jazz': '#9b59b6',
            'Blues': '#34495e',
            'Folk': '#27ae60',
            'Classical': '#f39c12',
            'Electronic': '#e67e22',
            'Country': '#95a5a6'
        }
        color = colors.get(obj.genero, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.genero
        )
    genero_badge.short_description = 'Género'
    genero_badge.admin_order_field = 'genero'
    
    def dificultad_badge(self, obj):
        """Muestra la dificultad como badge"""
        colors = {
            'Fácil': '#27ae60',
            'Intermedio': '#f39c12',
            'Difícil': '#e74c3c',
            'Experto': '#8e44ad'
        }
        color = colors.get(obj.dificultad, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 10px;">{}</span>',
            color, obj.dificultad
        )
    dificultad_badge.short_description = 'Dificultad'
    dificultad_badge.admin_order_field = 'dificultad'
    
    def favorita_badge(self, obj):
        """Muestra si la canción es favorita"""
        if obj.es_favorita:
            return format_html(
                '<span style="color: #f39c12; font-size: 14px;">★</span>'
            )
        return format_html(
            '<span style="color: #bdc3c7; font-size: 14px;">☆</span>'
        )
    favorita_badge.short_description = 'Favorita'
    favorita_badge.admin_order_field = 'es_favorita'
    
    def tiene_recursos_badge(self, obj):
        """Muestra si la canción tiene recursos (enlaces)"""
        if obj.tiene_recursos:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">✓</span>'
            )
        return format_html(
            '<span style="color: #e74c3c; font-weight: bold;">✗</span>'
        )
    tiene_recursos_badge.short_description = 'Recursos'
    tiene_recursos_badge.admin_order_field = 'link'
    
    def get_list_display(self, request):
        """Personaliza los campos mostrados según los permisos del usuario"""
        list_display = list(self.list_display)
        
        if not request.user.has_perm('repertorie.change_repertorio'):
            # Si no puede editar, ocultar algunos campos sensibles
            if 'veces_tocada' in list_display:
                list_display.remove('veces_tocada')
        
        return list_display
    
    def save_model(self, request, obj, form, change):
        """Lógica personalizada al guardar el modelo"""
        # Si es una nueva canción, establecer valores por defecto
        if not change:
            obj.veces_tocada = 0
        
        super().save_model(request, obj, form, change)
    
    # Acciones personalizadas
    def mark_as_favorite(self, request, queryset):
        """Marca las canciones seleccionadas como favoritas"""
        updated = 0
        for song in queryset:
            song.marcar_favorita()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} canción(es) marcada(s) como favorita(s).'
        )
    mark_as_favorite.short_description = "Marcar como favoritas"
    
    def remove_favorite(self, request, queryset):
        """Quita las canciones seleccionadas de favoritas"""
        updated = 0
        for song in queryset:
            song.quitar_favorita()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} canción(es) quitada(s) de favoritas.'
        )
    remove_favorite.short_description = "Quitar de favoritas"
    
    def mark_as_played(self, request, queryset):
        """Marca las canciones seleccionadas como tocadas"""
        updated = 0
        for song in queryset:
            song.marcar_como_tocada()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} canción(es) marcada(s) como tocada(s).'
        )
    mark_as_played.short_description = "Marcar como tocadas"
    
    def reset_play_count(self, request, queryset):
        """Reinicia el contador de reproducciones"""
        updated = queryset.update(veces_tocada=0, ultima_vez_tocada=None)
        
        self.message_user(
            request,
            f'Contador de reproducciones reiniciado para {updated} canción(es).'
        )
    reset_play_count.short_description = "Reiniciar contador de reproducciones"
    
    def restore_songs(self, request, queryset):
        """Restaura canciones eliminadas (soft delete)"""
        updated = queryset.filter(is_active=False).update(
            is_active=True,
            deleted_at=None
        )
        
        self.message_user(
            request,
            f'{updated} canción(es) restaurada(s).'
        )
    restore_songs.short_description = "Restaurar canciones eliminadas"
