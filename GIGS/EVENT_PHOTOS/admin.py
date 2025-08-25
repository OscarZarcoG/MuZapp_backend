from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import EventPhoto


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    """Configuración del admin para EventPhoto"""
    
    list_display = [
        'nombre_foto', 'evento', 'cliente_link', 'tipo_evento_badge',
        'fecha_evento', 'fotografo', 'publicas_badge', 'destacadas_badge',
        'tamaño_archivo_display', 'created_at'
    ]
    
    list_filter = [
        'tipo_evento', 'publicas', 'destacadas', 'fecha_evento',
        'created_at', 'is_active'
    ]
    
    search_fields = [
        'nombre_foto', 'evento', 'descripcion', 'ubicacion',
        'fotografo', 'cliente__nombre', 'cliente__apellido'
    ]
    
    readonly_fields = [
        'id', 'ancho_imagen', 'alto_imagen', 'tamaño_archivo',
        'tamaño_archivo_mb', 'resolucion', 'es_horizontal',
        'es_cuadrada', 'dias_desde_evento', 'url_foto',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre_foto', 'foto', 'fecha_foto', 'descripcion'
            )
        }),
        ('Detalles del Evento', {
            'fields': (
                'evento', 'fecha_evento', 'tipo_evento', 'ubicacion'
            )
        }),
        ('Relaciones', {
            'fields': (
                'cliente', 'contrato', 'fotografo'
            )
        }),
        ('Configuración de Visibilidad', {
            'fields': (
                'publicas', 'destacadas'
            )
        }),
        ('Metadatos de Imagen', {
            'fields': (
                'ancho_imagen', 'alto_imagen', 'tamaño_archivo',
                'tamaño_archivo_mb', 'resolucion', 'es_horizontal',
                'es_cuadrada'
            ),
            'classes': ('collapse',)
        }),
        ('Información Calculada', {
            'fields': (
                'dias_desde_evento', 'url_foto'
            ),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': (
                'id', 'is_active', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-fecha_evento', '-created_at']
    date_hierarchy = 'fecha_evento'
    
    # Acciones personalizadas
    actions = [
        'mark_as_public', 'mark_as_private', 'mark_as_featured',
        'remove_featured', 'restore_photos'
    ]
    
    def get_queryset(self, request):
        """Incluir elementos eliminados y optimizar consultas"""
        return EventPhoto.objects.select_related(
            'cliente', 'contrato'
        ).prefetch_related(
            'cliente__telefono_set'
        )
    
    def cliente_link(self, obj):
        """Enlace al cliente relacionado"""
        if obj.cliente:
            url = reverse('admin:CLIENTS_client_change', args=[obj.cliente.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.cliente.nombre_completo
            )
        return '-'
    cliente_link.short_description = 'Cliente'
    cliente_link.admin_order_field = 'cliente__nombre'
    
    def tipo_evento_badge(self, obj):
        """Badge colorido para el tipo de evento"""
        colors = {
            'boda': '#e74c3c',
            'cumpleanos': '#f39c12',
            'corporativo': '#3498db',
            'quinceanos': '#e91e63',
            'graduacion': '#9b59b6',
            'bautizo': '#1abc9c',
            'otro': '#95a5a6'
        }
        color = colors.get(obj.tipo_evento, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_evento_display()
        )
    tipo_evento_badge.short_description = 'Tipo de Evento'
    tipo_evento_badge.admin_order_field = 'tipo_evento'
    
    def publicas_badge(self, obj):
        """Badge para fotos públicas"""
        if obj.publicas:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px;">PÚBLICA</span>'
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 10px;">PRIVADA</span>'
        )
    publicas_badge.short_description = 'Visibilidad'
    publicas_badge.admin_order_field = 'publicas'
    
    def destacadas_badge(self, obj):
        """Badge para fotos destacadas"""
        if obj.destacadas:
            return format_html(
                '<span style="background-color: #f39c12; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px;">⭐ DESTACADA</span>'
            )
        return '-'
    destacadas_badge.short_description = 'Destacada'
    destacadas_badge.admin_order_field = 'destacadas'
    
    def tamaño_archivo_display(self, obj):
        """Mostrar tamaño del archivo en formato legible"""
        if obj.tamaño_archivo:
            mb = obj.tamaño_archivo_mb
            if mb >= 1:
                return f'{mb:.1f} MB'
            else:
                kb = obj.tamaño_archivo / 1024
                return f'{kb:.1f} KB'
        return '-'
    tamaño_archivo_display.short_description = 'Tamaño'
    tamaño_archivo_display.admin_order_field = 'tamaño_archivo'
    
    def get_list_display(self, request):
        """Personalizar campos mostrados según permisos"""
        list_display = list(self.list_display)
        if not request.user.has_perm('EVENT_PHOTOS.change_eventphoto'):
            # Remover campos sensibles para usuarios sin permisos de edición
            if 'cliente_link' in list_display:
                list_display.remove('cliente_link')
        return list_display
    
    def save_model(self, request, obj, form, change):
        """Lógica personalizada al guardar"""
        # Aquí se puede agregar lógica adicional antes de guardar
        super().save_model(request, obj, form, change)
    
    # Acciones personalizadas
    
    def mark_as_public(self, request, queryset):
        """Marcar fotos como públicas"""
        updated = 0
        for photo in queryset:
            photo.hacer_publica()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} foto(s) marcada(s) como pública(s).'
        )
    mark_as_public.short_description = 'Marcar como públicas'
    
    def mark_as_private(self, request, queryset):
        """Marcar fotos como privadas"""
        updated = 0
        for photo in queryset:
            photo.hacer_privada()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} foto(s) marcada(s) como privada(s).'
        )
    mark_as_private.short_description = 'Marcar como privadas'
    
    def mark_as_featured(self, request, queryset):
        """Marcar fotos como destacadas"""
        updated = 0
        for photo in queryset:
            photo.marcar_como_destacada()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} foto(s) marcada(s) como destacada(s).'
        )
    mark_as_featured.short_description = 'Marcar como destacadas'
    
    def remove_featured(self, request, queryset):
        """Quitar fotos de destacadas"""
        updated = 0
        for photo in queryset:
            photo.quitar_destacada()
            updated += 1
        
        self.message_user(
            request,
            f'{updated} foto(s) removida(s) de destacadas.'
        )
    remove_featured.short_description = 'Quitar de destacadas'
    
    def restore_photos(self, request, queryset):
        """Restaurar fotos eliminadas"""
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(
            request,
            f'{updated} foto(s) restaurada(s).'
        )
    restore_photos.short_description = 'Restaurar fotos eliminadas'
