""" 
from django.contrib import admin
from .models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'telefono', 'email', 'tipo_cliente', 'frecuencia', 'is_active', 'created_at')
    list_filter = ('is_active', 'tipo_cliente', 'frecuencia', 'ciudad', 'created_at')
    search_fields = ('nombre', 'apellidos', 'telefono', 'email', 'empresa')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellidos', 'tipo_cliente')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'ciudad', 'codigo_postal')
        }),
        ('Información Empresarial', {
            'fields': ('empresa', 'nif_cif'),
            'classes': ('collapse',)
        }),
        ('Otros Datos', {
            'fields': ('redes_sociales', 'frecuencia', 'observaciones')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Equipo_Audio)
class EquipoAudioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'marca', 'modelo', 'estado', 'precio_compra', 'is_active', 'created_at')
    list_filter = ('is_active', 'tipo', 'estado', 'marca', 'created_at')
    search_fields = ('nombre', 'marca', 'modelo', 'numero_serie', 'observaciones')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'estado')
        }),
        ('Detalles del Equipo', {
            'fields': ('marca', 'modelo', 'numero_serie', 'ubicacion')
        }),
        ('Información Financiera', {
            'fields': ('precio_compra', 'fecha_compra', 'garantia_hasta')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Campos Legacy', {
            'fields': ('numero_bocinas', 'descripcion'),
            'classes': ('collapse',),
            'description': 'Campos mantenidos por compatibilidad'
        }),
        ('Estado del Sistema', {
            'fields': ('is_active',)
        }),
        ('Fechas del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Catering)
class CateringAdmin(admin.ModelAdmin):
    list_display = ('peticion_grupo', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('peticion_grupo',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Peticion)
class PeticionAdmin(admin.ModelAdmin):
    list_display = ('nombre_cancion', 'link', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nombre_cancion',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Repertorio)
class RepertorioAdmin(admin.ModelAdmin):
    list_display = ('nombre_cancion', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nombre_cancion',)
    ordering = ('nombre_cancion',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(Fotos_Evento)
class FotosEventoAdmin(admin.ModelAdmin):
    list_display = ('nombre_foto', 'fecha_foto', 'is_active', 'created_at')
    list_filter = ('is_active', 'fecha_foto', 'created_at')
    search_fields = ('nombre_foto',)
    ordering = ('-fecha_foto',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    
    fieldsets = (
        ('Información de la Foto', {
            'fields': ('nombre_foto', 'fecha_foto', 'foto')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )


class PeticionInline(admin.TabularInline):
    model = Contrato.peticiones_cliente.through
    extra = 1


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_contrato', 'titulo', 'cliente', 'fecha_evento', 
        'estado_evento', 'pago_total', 'porcentaje', 'is_active'
    )
    list_filter = (
        'estado_evento', 'tipo_evento', 'fecha_evento', 
        'is_active', 'created_at'
    )
    search_fields = (
        'numero_contrato', 'titulo', 'nombre_festejado', 
        'cliente__nombre_cliente'
    )
    ordering = ('-fecha_evento', '-created_at')
    readonly_fields = (
        'numero_contrato', 'tiempo_total', 'pago_total', 
        'pago_restante', 'porcentaje', 'created_at', 
        'updated_at', 'deleted_at'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_contrato', 'titulo', 'tipo_evento', 
                'nombre_festejado', 'estado_evento', 'notas'
            )
        }),
        ('Fecha y Hora', {
            'fields': (
                'fecha_evento', 'hora_inicio', 'hora_final', 'tiempo_total'
            )
        }),
        ('Cliente y Audiencia', {
            'fields': ('cliente', 'audiencia')
        }),
        ('Lugar', {
            'fields': (
                'nombre_lugar', 'descripcion_lugar', 
                'google_maps_url', 'fotos_lugar'
            )
        }),
        ('Descansos', {
            'fields': (
                'oportunidades_descanso', 'tiempo_descanso', 
                'descripcion_descanso'
            ),
            'classes': ('collapse',)
        }),
        ('Información Financiera', {
            'fields': (
                'costo_hora', 'pago_adelanto', 'costo_extra',
                'pago_total', 'pago_restante', 'porcentaje'
            )
        }),
        ('Servicios', {
            'fields': ('equipo_audio', 'catering')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas del Sistema', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ('peticiones_cliente',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cliente', 'equipo_audio', 'catering'
        ).prefetch_related('peticiones_cliente')
    
    actions = ['marcar_como_confirmado', 'marcar_como_completado', 'marcar_como_cancelado']
    
    def marcar_como_confirmado(self, request, queryset):
        queryset.update(estado_evento='confirmed')
        self.message_user(request, f'{queryset.count()} contratos marcados como confirmados.')
    marcar_como_confirmado.short_description = 'Marcar como confirmado'
    
    def marcar_como_completado(self, request, queryset):
        queryset.update(estado_evento='completed')
        self.message_user(request, f'{queryset.count()} contratos marcados como completados.')
    marcar_como_completado.short_description = 'Marcar como completado'
    
    def marcar_como_cancelado(self, request, queryset):
        queryset.update(estado_evento='cancelled')
        self.message_user(request, f'{queryset.count()} contratos marcados como cancelados.')
    marcar_como_cancelado.short_description = 'Marcar como cancelado'



"""