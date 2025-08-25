from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Configuración del admin para Contract"""
    
    list_display = [
        'numero_contrato', 'titulo', 'cliente_link', 'fecha_evento',
        'estado_badge', 'pago_total', 'audiencia', 'dias_hasta_evento',
        'created_at'
    ]
    
    list_filter = [
        'estado_evento', 'tipo_evento', 'fecha_evento', 'created_at',
        'pago_total', 'audiencia', 'is_active'
    ]
    
    search_fields = [
        'numero_contrato', 'titulo', 'nombre_festejado', 'nombre_lugar',
        'cliente__nombre', 'cliente__apellidos', 'cliente__email',
        'notas', 'descripcion_lugar'
    ]
    
    readonly_fields = [
        'numero_contrato', 'tiempo_total', 'pago_restante',
        'created_at', 'updated_at', 'duracion_horas',
        'esta_proximo', 'esta_vencido', 'dias_hasta_evento'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_contrato', 'titulo', 'tipo_evento',
                'nombre_festejado', 'estado_evento', 'notas'
            )
        }),
        ('Cliente y Relaciones', {
            'fields': (
                'cliente', 'equipo_audio', 'catering', 'peticiones_cliente'
            )
        }),
        ('Fecha y Horario', {
            'fields': (
                'fecha_evento', 'hora_inicio', 'hora_final',
                'tiempo_total', 'dias_hasta_evento'
            )
        }),
        ('Descansos', {
            'fields': (
                'oportunidades_descanso', 'tiempo_descanso',
                'descripcion_descanso'
            ),
            'classes': ('collapse',)
        }),
        ('Ubicación', {
            'fields': (
                'nombre_lugar', 'descripcion_lugar',
                'google_maps_url', 'fotos_lugar'
            )
        }),
        ('Información Financiera', {
            'fields': (
                'pago_total', 'costo_hora', 'pago_adelanto',
                'pago_restante', 'porcentaje', 'costo_extra'
            )
        }),
        ('Audiencia', {
            'fields': ('audiencia',)
        }),
        ('Información del Sistema', {
            'fields': (
                'is_active', 'created_at', 'updated_at',
                'duracion_horas', 'esta_proximo', 'esta_vencido'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-fecha_evento', '-created_at']
    date_hierarchy = 'fecha_evento'
    list_per_page = 25
    
    actions = [
        'mark_as_confirmed', 'mark_as_in_progress',
        'mark_as_completed', 'mark_as_cancelled',
        'restore_contracts'
    ]
    
    def get_queryset(self, request):
        """Incluir contratos eliminados y optimizar consultas"""
        return super().get_queryset(request).select_related(
            'cliente', 'equipo_audio', 'catering'
        ).prefetch_related('peticiones_cliente')
    
    def cliente_link(self, obj):
        """Link al cliente relacionado"""
        if obj.cliente:
            url = reverse('admin:CLIENTS_client_change', args=[obj.cliente.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                f"{obj.cliente.nombre} {obj.cliente.apellidos}"
            )
        return '-'
    cliente_link.short_description = 'Cliente'
    cliente_link.admin_order_field = 'cliente__nombre'
    
    def estado_badge(self, obj):
        """Badge colorido para el estado"""
        colors = {
            'pending': '#ffc107',      # Amarillo
            'confirmed': '#28a745',    # Verde
            'in_progress': '#007bff',  # Azul
            'completed': '#6c757d',    # Gris
            'cancelled': '#dc3545'     # Rojo
        }
        
        labels = {
            'pending': 'Pendiente',
            'confirmed': 'Confirmado',
            'in_progress': 'En Progreso',
            'completed': 'Completado',
            'cancelled': 'Cancelado'
        }
        
        color = colors.get(obj.estado_evento, '#6c757d')
        label = labels.get(obj.estado_evento, obj.estado_evento.title())
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, label
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado_evento'
    
    def dias_hasta_evento(self, obj):
        """Días restantes hasta el evento con colores"""
        if not obj.fecha_evento:
            return '-'
        
        dias = obj.dias_hasta_evento()
        
        if dias < 0:
            color = '#dc3545'  # Rojo - evento pasado
            text = f'{abs(dias)} días atrás'
        elif dias == 0:
            color = '#ffc107'  # Amarillo - hoy
            text = 'Hoy'
        elif dias <= 7:
            color = '#fd7e14'  # Naranja - próxima semana
            text = f'{dias} días'
        elif dias <= 30:
            color = '#28a745'  # Verde - próximo mes
            text = f'{dias} días'
        else:
            color = '#6c757d'  # Gris - futuro lejano
            text = f'{dias} días'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    dias_hasta_evento.short_description = 'Días hasta evento'
    dias_hasta_evento.admin_order_field = 'fecha_evento'
    
    # Acciones personalizadas
    def mark_as_confirmed(self, request, queryset):
        """Marcar contratos como confirmados"""
        updated = 0
        for contract in queryset:
            try:
                contract.confirmar()
                updated += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f'{updated} contrato(s) marcado(s) como confirmado(s).'
        )
    mark_as_confirmed.short_description = 'Marcar como confirmado'
    
    def mark_as_in_progress(self, request, queryset):
        """Marcar contratos como en progreso"""
        updated = 0
        for contract in queryset:
            try:
                contract.iniciar()
                updated += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f'{updated} contrato(s) marcado(s) como en progreso.'
        )
    mark_as_in_progress.short_description = 'Marcar como en progreso'
    
    def mark_as_completed(self, request, queryset):
        """Marcar contratos como completados"""
        updated = 0
        for contract in queryset:
            try:
                contract.completar()
                updated += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f'{updated} contrato(s) marcado(s) como completado(s).'
        )
    mark_as_completed.short_description = 'Marcar como completado'
    
    def mark_as_cancelled(self, request, queryset):
        """Marcar contratos como cancelados"""
        updated = 0
        for contract in queryset:
            try:
                contract.cancelar('Cancelado desde admin')
                updated += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f'{updated} contrato(s) marcado(s) como cancelado(s).'
        )
    mark_as_cancelled.short_description = 'Marcar como cancelado'
    
    def restore_contracts(self, request, queryset):
        """Restaurar contratos eliminados"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} contrato(s) restaurado(s).'
        )
    restore_contracts.short_description = 'Restaurar contratos'
    
    def get_list_display(self, request):
        """Personalizar campos mostrados según permisos"""
        list_display = list(self.list_display)
        
        # Si el usuario no tiene permisos para ver clientes, ocultar el link
        if not request.user.has_perm('CLIENTS.view_client'):
            if 'cliente_link' in list_display:
                list_display[list_display.index('cliente_link')] = 'cliente'
        
        return list_display
    
    def save_model(self, request, obj, form, change):
        """Personalizar guardado del modelo"""
        if not change:  # Nuevo contrato
            # Aquí se podría agregar lógica adicional para nuevos contratos
            pass
        
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/contract_admin.css',)
        }
        js = ('admin/js/contract_admin.js',)
