from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    BookingEvent, ContractSignature, EventPhoto,
    VenueTemplate, AudioTemplate, ContractTemplate
)


class ContractSignatureInline(admin.TabularInline):
    model = ContractSignature
    extra = 0
    readonly_fields = ['signed_at', 'ip_address']

    def has_change_permission(self, request, obj=None):
        return False


class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 0
    readonly_fields = ['created_at']
    fields = ['image', 'description', 'is_featured', 'created_at']


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = [
        'contract_number', 'title', 'client_name', 'date',
        'start_time', 'status_badge', 'payment_info', 'created_by'
    ]
    list_filter = [
        'status', 'event_type', 'date', 'created_at',
        'assigned_to', 'created_by'
    ]
    search_fields = [
        'contract_number', 'title', 'client_name',
        'celebrant_name', 'venue_name'
    ]
    readonly_fields = [
        'contract_number', 'tiempo_total', 'total_payment',
        'created_at', 'updated_at', 'contract_generated_at',
        'duration_display', 'payment_summary'
    ]
    inlines = [ContractSignatureInline, EventPhotoInline]

    fieldsets = (
        ('Información Básica', {
            'fields': (
                'contract_number', 'title', 'event_type',
                'celebrant_name', 'description', 'status'
            )
        }),
        ('Fecha y Horario', {
            'fields': (
                'date', 'start_time', 'end_time',
                'tiempo_total', 'duration_display'
            )
        }),
        ('Descansos', {
            'fields': ('break_opportunity', 'break_times')
        }),
        ('Lugar', {
            'fields': (
                'venue_name', 'venue_description', 'venue_dimensions',
                'venue_capacity', 'google_maps_url', 'waze_url'
            )
        }),
        ('Cliente', {
            'fields': (
                'client_name', 'client_phone', 'client_social_media'
            )
        }),
        ('Audiencia y Requerimientos', {
            'fields': (
                'expected_audience', 'audio_description',
                'backstage_requirements'
            )
        }),
        ('Música', {
            'fields': ('client_song_requests', 'song_links')
        }),
        ('Información Financiera', {
            'fields': (
                'hourly_rate', 'total_payment', 'advance_payment',
                'payment_summary'
            )
        }),
        ('Asignación', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Contrato', {
            'fields': (
                'contract_terms', 'contract_file',
                'contract_generated_at'
            )
        }),
        ('Notas', {
            'fields': ('additional_notes',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'under_review': '#17a2b8',
            'confirmed': '#28a745',
            'in_progress': '#007bff',
            'completed': '#6f42c1',
            'cancelled': '#dc3545',
            'contract_generated': '#fd7e14',
            'signed': '#20c997'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )

    status_badge.short_description = 'Estado'

    def payment_info(self, obj):
        if obj.total_payment:
            percentage = obj.payment_percentage
            return format_html(
                '${:,.2f} ({}%)',
                obj.total_payment,
                int(percentage)
            )
        return '-'

    payment_info.short_description = 'Pago'

    def duration_display(self, obj):
        return obj.get_formatted_duration()

    duration_display.short_description = 'Duración'

    def payment_summary(self, obj):
        if obj.total_payment:
            html = f"""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                <strong>Total:</strong> ${obj.total_payment:,.2f}<br>
                <strong>Adelanto:</strong> ${obj.advance_payment:,.2f}<br>
                <strong>Pendiente:</strong> ${obj.pending_payment:,.2f}<br>
                <strong>Porcentaje pagado:</strong> {obj.payment_percentage:.1f}%
            </div>
            """
            return mark_safe(html)
        return 'No definido'

    payment_summary.short_description = 'Resumen de Pagos'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContractSignature)
class ContractSignatureAdmin(admin.ModelAdmin):
    list_display = [
        'event', 'signature_type', 'signed_by',
        'signed_at', 'ip_address'
    ]
    list_filter = ['signature_type', 'signed_at']
    search_fields = ['event__contract_number', 'signed_by__username']
    readonly_fields = ['signed_at', 'ip_address']

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = [
        'event', 'description', 'is_featured',
        'created_at', 'image_preview'
    ]
    list_filter = ['is_featured', 'created_at']
    search_fields = ['event__title', 'description']
    readonly_fields = ['created_at', 'image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return 'Sin imagen'

    image_preview.short_description = 'Vista previa'


@admin.register(VenueTemplate)
class VenueTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'capacity', 'is_active', 'usage_count'
    ]
    list_filter = ['is_active', 'capacity']
    search_fields = ['name', 'address']

    def usage_count(self, obj):
        return BookingEvent.objects.filter(venue_name=obj.name).count()

    usage_count.short_description = 'Usos'


@admin.register(AudioTemplate)
class AudioTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'usage_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

    def usage_count(self, obj):
        return BookingEvent.objects.filter(
            audio_description__icontains=obj.name
        ).count()

    usage_count.short_description = 'Usos'


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_default', 'is_active',
        'created_at', 'updated_at'
    ]
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        # Asegurar que solo haya una plantilla por defecto
        if obj.is_default:
            ContractTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save_model(request, obj, form, change)