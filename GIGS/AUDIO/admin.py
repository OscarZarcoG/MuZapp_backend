# GIGS/AUDIO/admin.py
from django.contrib import admin
from .models import AudioEquipment

@admin.register(AudioEquipment)
class AudioEquipmentAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'tipo', 'marca', 'modelo', 'estado', 'cantidad_equipo',
        'ubicacion', 'precio_compra', 'fecha_compra', 'is_active'
    )
    list_filter = (
        'tipo', 'estado', 'marca', 'fecha_compra', 
        'is_active', 'created_at'
    )
    search_fields = (
        'nombre', 'marca', 'modelo', 'numero_serie', 
        'descripcion', 'ubicacion'
    )
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'deleted_at',
        'nombre_completo', 'esta_disponible', 'necesita_mantenimiento'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre', 'tipo', 'marca', 'modelo', 'numero_serie'
            )
        }),
        ('Estado y Ubicación', {
            'fields': (
                'estado', 'ubicacion', 'observaciones'
            )
        }),
        ('Información Comercial', {
            'fields': (
                'precio_compra', 'fecha_compra', 'garantia_hasta'
            ),
        }),
        ('Detalles Técnicos', {
            'fields': (
                'cantidad_equipo', 'descripcion', 'imagen'
            ),
        }),
        ('Información del Sistema', {
            'fields': (
                'id', 'is_active', 'created_at', 'updated_at', 'deleted_at',
                'nombre_completo', 'esta_disponible', 'necesita_mantenimiento'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_available', 'mark_as_maintenance', 'mark_as_in_use']
    
    def mark_as_available(self, request, queryset):
        """Marcar equipos seleccionados como disponibles"""
        updated = queryset.update(estado='disponible')
        self.message_user(
            request, 
            f'{updated} equipo(s) marcado(s) como disponible(s).'
        )
    mark_as_available.short_description = "Marcar como disponible"
    
    def mark_as_maintenance(self, request, queryset):
        """Marcar equipos seleccionados como en mantenimiento"""
        updated = queryset.update(estado='mantenimiento')
        self.message_user(
            request, 
            f'{updated} equipo(s) marcado(s) como en mantenimiento.'
        )
    mark_as_maintenance.short_description = "Marcar como en mantenimiento"
    
    def mark_as_in_use(self, request, queryset):
        """Marcar equipos seleccionados como en uso"""
        updated = queryset.filter(estado='disponible').update(estado='en_uso')
        self.message_user(
            request, 
            f'{updated} equipo(s) disponible(s) marcado(s) como en uso.'
        )
    mark_as_in_use.short_description = "Marcar como en uso (solo disponibles)"

