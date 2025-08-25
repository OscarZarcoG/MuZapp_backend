# GIGS/CLIENTS/models.py
from django.db import models
from core.models import BaseModel, BaseModelManager

class ClientManager(BaseModelManager):
    def active_clients(self):
        return self.filter(is_active=True)
    

class Client(BaseModel):
    objects = ClientManager()

    TIPO_CLIENTE_CHOICES = [
        ('particular', 'Particular'),
        ('empresa', 'Empresa'),
        ('organizacion', 'Organización'),
    ]
    
    FRECUENCIA_CHOICES = [
        ('frecuente', 'Frecuente'),
        ('regular', 'Regular'),
        ('ocasional', 'Ocasional'),
    ]
    
    # Información personal
    nombre = models.CharField(
        max_length=255,
        verbose_name="Nombre",
        help_text="Nombre del cliente"
    )
    apellidos = models.CharField(
        max_length=255,
        verbose_name="Apellidos",
        blank=True,
        help_text="Apellidos del cliente"
    )
    
    # Información de contacto
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Número de teléfono del cliente"
    )
    email = models.EmailField(
        verbose_name="Email",
        blank=True,
        help_text="Correo electrónico del cliente"
    )
    redes_sociales = models.URLField(
        verbose_name="Redes sociales",
        blank=True,
        help_text="Enlaces a redes sociales del cliente"
    )
    
    # Dirección
    direccion = models.CharField(
        max_length=500,
        verbose_name="Dirección",
        blank=True,
        help_text="Dirección completa del cliente"
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name="Ciudad",
        blank=True,
        help_text="Ciudad del cliente"
    )
    codigo_postal = models.CharField(
        max_length=10,
        verbose_name="Código Postal",
        blank=True,
        help_text="Código postal del cliente"
    )
    
    # Tipo de cliente
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='particular',
        verbose_name="Tipo de Cliente",
        help_text="Tipo de cliente: particular, empresa u organización"
    )
    
    # Información empresarial (opcional)
    empresa = models.CharField(
        max_length=255,
        verbose_name="Empresa/Organización",
        blank=True,
        help_text="Nombre de la empresa u organización (si aplica)"
    )
    nif_cif = models.CharField(
        max_length=20,
        verbose_name="NIF/CIF",
        blank=True,
        help_text="Número de identificación fiscal (si aplica)"
    )
    
    # Observaciones
    observaciones = models.TextField(
        verbose_name="Observaciones",
        blank=True,
        help_text="Notas adicionales sobre el cliente"
    )
    frecuencia = models.CharField(
        max_length=20,
        choices=FRECUENCIA_CHOICES,
        default='ocasional',
        verbose_name="Frecuencia",
        help_text="Frecuencia de contratación del cliente"
    )
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre', 'apellidos']
    
    def __str__(self):
        if self.apellidos:
            return f"{self.nombre} {self.apellidos}"
        return self.nombre
    
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del cliente"""
        if self.apellidos:
            return f"{self.nombre} {self.apellidos}"
        return self.nombre
    
    @property
    def es_empresa(self):
        """Indica si el cliente es una empresa u organización"""
        return self.tipo_cliente in ['empresa', 'organizacion']