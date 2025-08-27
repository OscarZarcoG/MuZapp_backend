from django.contrib import admin
from .models import Pais, Estado, Municipio, Colonia


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'pais']
    list_filter = ['pais']
    search_fields = ['nombre', 'pais__nombre']
    ordering = ['pais__nombre', 'nombre']
    autocomplete_fields = ['pais']


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'estado', 'get_pais']
    list_filter = ['estado__pais', 'estado']
    search_fields = ['nombre', 'estado__nombre', 'estado__pais__nombre']
    ordering = ['estado__pais__nombre', 'estado__nombre', 'nombre']
    autocomplete_fields = ['estado']
    
    def get_pais(self, obj):
        return obj.estado.pais.nombre
    get_pais.short_description = 'País'
    get_pais.admin_order_field = 'estado__pais__nombre'


@admin.register(Colonia)
class ColoniaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'ciudad', 'codigo_postal', 'municipio', 'asentamiento']
    list_filter = ['asentamiento', 'municipio__estado__pais', 'municipio__estado']
    search_fields = ['nombre', 'ciudad', 'codigo_postal', 'municipio__nombre']
    ordering = ['municipio__estado__pais__nombre', 'municipio__estado__nombre', 'municipio__nombre', 'nombre']
    autocomplete_fields = ['municipio']
    list_per_page = 50
