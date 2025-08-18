# AUTH/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserCustom


@admin.register(UserCustom)
class UserCustomAdmin(UserAdmin):
    # Campos que se muestran en la lista
    list_display = (
        'username',
        'get_full_name',
        'email',
        'phone',
        'role',
        'gender',
        'is_active',
        'is_staff',
        'created_at',
        'profile_image_preview'
    )
    
    # Campos por los que se puede filtrar
    list_filter = (
        'role',
        'gender',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
        'updated_at',
    )
    
    # Campos de búsqueda
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'phone',
    )
    
    # Ordenamiento por defecto
    ordering = ('-created_at',)
    
    # Campos editables desde la lista
    list_editable = ('is_active', 'role')
    
    # Número de elementos por página
    list_per_page = 25
    
    # Campos de solo lectura
    readonly_fields = (
        'created_at',
        'updated_at',
        'last_login',
        'date_joined',
        'profile_image_preview'
    )
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'phone',
                'birthday',
                'gender'
            )
        }),
        ('Imagen de Perfil', {
            'fields': ('image_profile', 'profile_image_preview'),
            'classes': ('collapse',)
        }),
        ('Permisos y Roles', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Contraseña', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': (
                'last_login',
                'date_joined',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets para agregar usuario
    add_fieldsets = (
        ('Información Básica', {
            'classes': ('wide',),
            'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'phone',
                'password1',
                'password2'
            )
        }),
        ('Información Adicional', {
            'classes': ('wide', 'collapse'),
            'fields': (
                'birthday',
                'gender',
                'image_profile',
                'role'
            )
        }),
        ('Permisos', {
            'classes': ('wide', 'collapse'),
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )
    
    # Métodos personalizados para mostrar información
    def get_full_name(self, obj):
        """Retorna el nombre completo del usuario"""
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Nombre Completo'
    get_full_name.admin_order_field = 'first_name'
    
    def profile_image_preview(self, obj):
        """Muestra una vista previa de la imagen de perfil"""
        if obj.image_profile:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.image_profile.url
            )
        return "Sin imagen"
    profile_image_preview.short_description = 'Vista Previa'
    
    # Acciones personalizadas
    actions = ['activate_users', 'deactivate_users', 'make_admin', 'make_client']
    
    def activate_users(self, request, queryset):
        """Activa usuarios seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} usuario(s) activado(s) exitosamente.'
        )
    activate_users.short_description = "Activar usuarios seleccionados"
    
    def deactivate_users(self, request, queryset):
        """Desactiva usuarios seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} usuario(s) desactivado(s) exitosamente.'
        )
    deactivate_users.short_description = "Desactivar usuarios seleccionados"
    
    def make_admin(self, request, queryset):
        """Convierte usuarios seleccionados en administradores"""
        updated = queryset.update(role='admin')
        self.message_user(
            request,
            f'{updated} usuario(s) convertido(s) en administrador(es).'
        )
    make_admin.short_description = "Hacer administradores"
    
    def make_client(self, request, queryset):
        """Convierte usuarios seleccionados en clientes"""
        updated = queryset.update(role='client')
        self.message_user(
            request,
            f'{updated} usuario(s) convertido(s) en cliente(s).'
        )
    make_client.short_description = "Hacer clientes"
    
    # Personalizar el título del admin
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo campos relacionados"""
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related('groups', 'user_permissions')
    
    # Personalizar permisos
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar usuarios"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Usuarios pueden editar su propio perfil, admins pueden editar otros"""
        if obj is None:
            return True
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'root']:
            return True
        return obj == request.user


# Personalizar el título del sitio admin
admin.site.site_header = "MuZapp - Panel de Administración"
admin.site.site_title = "MuZapp Admin"
admin.site.index_title = "Bienvenido al Panel de Administración de MuZapp"