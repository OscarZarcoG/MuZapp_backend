# GIGS/CATERING/admin.py
from django.contrib import admin
from .models import Catering

@admin.register(Catering)
class CateringAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tipo_evento', 'estado', 'numero_personas', 
        'presupuesto_estimado', 'proveedor', 'fecha_evento', 'is_active'
    )
    list_filter = (
        'estado', 'tipo_evento', 'proveedor', 'fecha_evento', 
        'is_active', 'created_at'
    )
    search_fields = (
        'peticion_grupo', 'tipo_evento', 'proveedor', 
        'ubicacion', 'notas_adicionales', 'contacto_proveedor'
    )
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'deleted_at',
        'esta_pendiente', 'esta_confirmado', 'puede_cancelar'
    )
    
    fieldsets = (
        ('Información del Evento', {
            'fields': (
                'tipo_evento', 'fecha_evento', 'ubicacion', 'numero_personas'
            )
        }),
        ('Petición y Estado', {
            'fields': (
                'peticion_grupo', 'estado', 'presupuesto_estimado'
            )
        }),
        ('Proveedor', {
            'fields': (
                'proveedor', 'contacto_proveedor'
            ),
            'classes': ('collapse',)
        }),
        ('Notas Adicionales', {
            'fields': (
                'notas_adicionales',
            ),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': (
                'id', 'is_active', 'created_at', 'updated_at', 'deleted_at',
                'esta_pendiente', 'esta_confirmado', 'puede_cancelar'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_as_completed']
    
    def mark_as_confirmed(self, request, queryset):
        """Marcar solicitudes seleccionadas como confirmadas"""
        updated = 0
        for catering in queryset:
            if catering.confirmar():
                updated += 1
        self.message_user(
            request, 
            f'{updated} solicitud(es) de catering confirmada(s).'
        )
    mark_as_confirmed.short_description = "Confirmar solicitudes"
    
    def mark_as_cancelled(self, request, queryset):
        """Marcar solicitudes seleccionadas como canceladas"""
        updated = 0
        for catering in queryset:
            if catering.cancelar():
                updated += 1
        self.message_user(
            request, 
            f'{updated} solicitud(es) de catering cancelada(s).'
        )
    mark_as_cancelled.short_description = "Cancelar solicitudes"
    
    def mark_as_completed(self, request, queryset):
        """Marcar solicitudes seleccionadas como completadas"""
        updated = 0
        for catering in queryset:
            if catering.completar():
                updated += 1
        self.message_user(
            request, 
            f'{updated} solicitud(es) de catering completada(s).'
        )
    mark_as_completed.short_description = "Completar solicitudes"
    
    def get_queryset(self, request):
        """Incluir solicitudes eliminadas (soft delete) en el admin"""
        return self.model.all_objects.get_queryset()
