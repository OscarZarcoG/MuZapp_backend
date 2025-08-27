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
    
    # Dirección estructurada basada en datos de México
    codigo_postal = models.CharField(
        max_length=10,
        verbose_name="Código Postal",
        blank=True,
        help_text="Código postal del cliente"
    )
    colonia = models.CharField(
        max_length=100,
        verbose_name="Colonia",
        blank=True,
        help_text="Colonia o asentamiento del cliente"
    )
    municipio = models.CharField(
        max_length=100,
        verbose_name="Municipio",
        blank=True,
        help_text="Municipio del cliente"
    )
    estado = models.CharField(
        max_length=100,
        verbose_name="Estado",
        blank=True,
        help_text="Estado del cliente"
    )
    pais = models.CharField(
        max_length=50,
        verbose_name="País",
        default="México",
        help_text="País del cliente"
    )
    direccion_completa = models.CharField(
        max_length=500,
        verbose_name="Dirección Completa",
        blank=True,
        help_text="Calle, número y referencias adicionales"
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


class ClienteSocialMedia(BaseModel):
    """Modelo para manejar múltiples redes sociales por cliente"""
    
    REDES_SOCIALES = [
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('pinterest', 'Pinterest'),
        ('snapchat', 'Snapchat'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('reddit', 'Reddit'),
        ('other', 'Otro'),
    ]
    
    cliente = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='redes_sociales',
        verbose_name="Cliente"
    )
    
    tipo_red_social = models.CharField(
        max_length=20,
        choices=REDES_SOCIALES,
        verbose_name="Tipo de red social",
        help_text="Tipo de red social"
    )
    
    enlace = models.URLField(
        verbose_name="Enlace",
        help_text="Enlace a la red social"
    )
    
    nombre_usuario = models.CharField(
        max_length=100,
        verbose_name="Nombre de usuario",
        blank=True,
        help_text="Nombre de usuario en la red social (opcional)"
    )
    
    class Meta:
        verbose_name = "Red Social del Cliente"
        verbose_name_plural = "Redes Sociales del Cliente"
        unique_together = ['cliente', 'tipo_red_social', 'enlace']
        ordering = ['cliente', 'tipo_red_social']
    
    def __str__(self):
        return f"{self.cliente.nombre_completo} - {self.get_tipo_red_social_display()}"