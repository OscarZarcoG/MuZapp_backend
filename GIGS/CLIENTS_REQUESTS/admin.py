from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import ClientRequest


@admin.register(ClientRequest)
class ClientRequestAdmin(admin.ModelAdmin):
    """Configuración del admin para ClientRequest"""
    
    list_display = [
        'nombre_cancion',
        'artista',
        'cliente_link',
        'estado_badge',
        'prioridad_badge',
        'fecha_solicitud',
        'fecha_necesaria',
        'dias_restantes',
        'is_active',
    ]
    
    list_filter = [
        'estado',
        'prioridad',
        'dificultad_estimada',
        'genero',
        'fecha_solicitud',
        'fecha_necesaria',
        'is_active',
        'cliente__tipo_cliente',
    ]
    
    search_fields = [
        'nombre_cancion',
        'artista',
        'album',
        'genero',
        'cliente__nombre',
        'cliente__apellidos',
        'cliente__email',
        'evento_relacionado__titulo',
        'notas_cliente',
    ]
    
    readonly_fields = [
        'fecha_solicitud',
        'fecha_respuesta',
        'dias_hasta_fecha_necesaria',
        'esta_pendiente',
        'esta_aprobada',
        'esta_rechazada',
        'es_urgente',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    
    fieldsets = (
        ('Información de la Canción', {
            'fields': (
                'nombre_cancion',
                'artista',
                'album',
                'genero',
                'link',
                'link_partitura',
            )
        }),
        ('Información del Cliente y Evento', {
            'fields': (
                'cliente',
                'evento_relacionado',
            )
        }),
        ('Estado y Prioridad', {
            'fields': (
                'estado',
                'prioridad',
                'fecha_necesaria',
                'dificultad_estimada',
                'tiempo_estimado_aprendizaje',
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_solicitud',
                'fecha_respuesta',
                'dias_hasta_fecha_necesaria',
            ),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': (
                'notas_cliente',
                'notas_internas',
                'motivo_rechazo',
            )
        }),
        ('Estados Calculados', {
            'fields': (
                'esta_pendiente',
                'esta_aprobada',
                'esta_rechazada',
                'es_urgente',
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at',
                'deleted_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-fecha_solicitud']
    date_hierarchy = 'fecha_solicitud'
    
    actions = [
        'mark_as_approved',
        'mark_as_rejected',
        'mark_as_in_repertoire',
        'mark_as_urgent',
        'mark_as_high_priority',
    ]
    
    def cliente_link(self, obj):
        """Link al cliente relacionado"""
        if obj.cliente:
            url = reverse('admin:CLIENTS_client_change', args=[obj.cliente.pk])
            return format_html('<a href="{}">{}</a>', url, obj.cliente)
        return '-'
    cliente_link.short_description = 'Cliente'
    
    def estado_badge(self, obj):
        """Badge colorizado para el estado"""
        colors = {
            'pendiente': '#ffc107',  # amarillo
            'aprobada': '#28a745',   # verde
            'rechazada': '#dc3545',  # rojo
            'en_repertorio': '#17a2b8',  # azul
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def prioridad_badge(self, obj):
        """Badge colorizado para la prioridad"""
        colors = {
            'urgente': '#dc3545',    # rojo
            'alta': '#fd7e14',       # naranja
            'media': '#ffc107',      # amarillo
            'baja': '#28a745',       # verde
        }
        color = colors.get(obj.prioridad, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'
    
    def dias_restantes(self, obj):
        """Días restantes hasta la fecha necesaria"""
        if obj.fecha_necesaria:
            dias = obj.dias_hasta_fecha_necesaria
            if dias < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">{} días (vencida)</span>',
                    abs(dias)
                )
            elif dias <= 7:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">{} días</span>',
                    dias
                )
            else:
                return f'{dias} días'
        return '-'
    dias_restantes.short_description = 'Días Restantes'
    
    def mark_as_approved(self, request, queryset):
        """Acción para aprobar peticiones"""
        count = 0
        for obj in queryset:
            if obj.estado == 'pendiente':
                obj.aprobar()
                count += 1
        
        self.message_user(
            request,
            f'{count} peticiones fueron aprobadas exitosamente.'
        )
    mark_as_approved.short_description = 'Aprobar peticiones seleccionadas'
    
    def mark_as_rejected(self, request, queryset):
        """Acción para rechazar peticiones"""
        count = 0
        for obj in queryset:
            if obj.estado == 'pendiente':
                obj.rechazar('Rechazada desde el admin')
                count += 1
        
        self.message_user(
            request,
            f'{count} peticiones fueron rechazadas exitosamente.'
        )
    mark_as_rejected.short_description = 'Rechazar peticiones seleccionadas'
    
    def mark_as_in_repertoire(self, request, queryset):
        """Acción para marcar como en repertorio"""
        count = 0
        for obj in queryset:
            if obj.estado == 'aprobada':
                obj.marcar_en_repertorio()
                count += 1
        
        self.message_user(
            request,
            f'{count} peticiones fueron marcadas como en repertorio.'
        )
    mark_as_in_repertoire.short_description = 'Marcar como en repertorio'
    
    def mark_as_urgent(self, request, queryset):
        """Acción para marcar como urgente"""
        count = queryset.update(prioridad='urgente')
        self.message_user(
            request,
            f'{count} peticiones fueron marcadas como urgentes.'
        )
    mark_as_urgent.short_description = 'Marcar como urgente'
    
    def mark_as_high_priority(self, request, queryset):
        """Acción para marcar como alta prioridad"""
        count = queryset.update(prioridad='alta')
        self.message_user(
            request,
            f'{count} peticiones fueron marcadas como alta prioridad.'
        )
    mark_as_high_priority.short_description = 'Marcar como alta prioridad'