from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import Client, ClienteSocialMedia
from .utils import autocompletar_inputs_de_direccion_por_codigo_postal

class ClienteSocialMediaInline(admin.TabularInline):
    model = ClienteSocialMedia
    extra = 1
    fields = ('tipo_red_social', 'enlace')
    verbose_name = "Red Social"
    verbose_name_plural = "Redes Sociales"

class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

    class Media:
        js = ('admin/js/autocomplete_cp.js',)

    def clean(self):
        cleaned_data = super().clean()
        codigo_postal = cleaned_data.get('codigo_postal')
        if codigo_postal:
            datos = autocompletar_inputs_de_direccion_por_codigo_postal(codigo_postal)
            if datos:
                # Si hay una sola colonia, autocompletar todo
                if 'colonia' in datos:
                    cleaned_data['colonia'] = datos.get('colonia', '')
                    cleaned_data['municipio'] = datos.get('municipio', '')
                    cleaned_data['estado'] = datos.get('estado', '')
                    cleaned_data['pais'] = datos.get('pais', '') or 'México'
                # Si hay varias colonias, solo municipio/estado/pais
                elif 'colonias' in datos:
                    cleaned_data['municipio'] = datos.get('municipio', '')
                    cleaned_data['estado'] = datos.get('estado', '')
                    cleaned_data['pais'] = datos.get('pais', '') or 'México'
        # Validar que país nunca quede vacío
        if not cleaned_data.get('pais'):
            cleaned_data['pais'] = 'México'
        return cleaned_data

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    inlines = [ClienteSocialMediaInline]
    list_display = (
        'nombre_completo', 'telefono', 'colonia', 'municipio', 'estado',
        'email', 'frecuencia'
    )
    list_filter = (
        'tipo_cliente', 'frecuencia', 'is_active', 
        'created_at', 'estado', 'municipio'
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
            'fields': ('codigo_postal', 'colonia', 'municipio', 'estado', 'pais')
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
