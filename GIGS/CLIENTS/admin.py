from django.contrib import admin
from .models import Client, ClienteSocialMedia


class ClienteSocialMediaInline(admin.TabularInline):
    model = ClienteSocialMedia
    extra = 1
    fields = ('tipo_red_social', 'enlace')
    verbose_name = "Red Social"
    verbose_name_plural = "Redes Sociales"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [ClienteSocialMediaInline]
    list_display = (
        'nombre_completo', 'telefono', 'direccion', 'observaciones',
        'email', 'frecuencia'
    )
    list_filter = (
        'tipo_cliente', 'frecuencia', 'is_active', 
        'created_at', 'ciudad'
    )
    search_fields = (
        'nombre', 'apellidos', 'email', 'telefono', 
        'empresa', 'nif_cif'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'deleted_at'
    )
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellidos', 'tipo_cliente')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'codigo_postal')
        }),
        ('Información Empresarial', {
            'fields': ('empresa', 'nif_cif'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones', 'frecuencia')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
    
    def nombre_completo(self, obj):
        return obj.nombre_completo
    nombre_completo.short_description = 'Nombre Completo'


@admin.register(ClienteSocialMedia)
class ClienteSocialMediaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_red_social', 'enlace', 'created_at')
    list_filter = ('tipo_red_social', 'created_at')
    search_fields = ('cliente__nombre', 'cliente__apellidos', 'enlace')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    
    fieldsets = (
        ('Información de la Red Social', {
            'fields': ('cliente', 'tipo_red_social', 'enlace')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
