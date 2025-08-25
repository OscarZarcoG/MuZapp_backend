# GIGS/AUDIO/models.py
from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel, BaseModelManager

class AudioEquipmentManager(BaseModelManager):
    def available_equipment(self):
        return self.filter(estado='disponible', is_active=True)
    
    def by_type(self, tipo):
        return self.filter(tipo=tipo, is_active=True)

class AudioEquipment(BaseModel):
    objects = AudioEquipmentManager()
    
    TIPO_EQUIPO_CHOICES = [
        ('altavoces', 'Altavoces'),
        ('microfonos', 'Micrófonos'),
        ('mezcladores', 'Mezcladores'),
        ('amplificadores', 'Amplificadores'),
        ('instrumentos', 'Instrumentos'),
        ('iluminacion', 'Iluminación'),
        ('cables', 'Cables'),
        ('soportes', 'Soportes'),
        ('otros', 'Otros'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_uso', 'En Uso'),
        ('mantenimiento', 'Mantenimiento'),
        ('averiado', 'Averiado'),
        ('vendido', 'Vendido'),
    ]
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Equipo",
        help_text="Nombre descriptivo del equipo de audio"
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_EQUIPO_CHOICES,
        default='altavoces',
        verbose_name="Tipo de Equipo",
        db_index=True
    )
    marca = models.CharField(
        max_length=200,
        verbose_name="Marca",
        blank=True,
        help_text="Marca del equipo"
    )
    modelo = models.CharField(
        max_length=200,
        verbose_name="Modelo",
        blank=True,
        help_text="Modelo específico del equipo"
    )
    numero_serie = models.CharField(
        max_length=200,
        verbose_name="Número de Serie",
        blank=True,
        unique=True,
        null=True,
        help_text="Número de serie único del equipo"
    )
    estado = models.CharField(
        max_length=50,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name="Estado",
        db_index=True
    )
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Compra",
        null=True,
        blank=True,
        help_text="Precio de compra del equipo"
    )
    fecha_compra = models.DateField(
        verbose_name="Fecha de Compra",
        null=True,
        blank=True,
        help_text="Fecha en que se adquirió el equipo"
    )
    garantia_hasta = models.DateField(
        verbose_name="Garantía Hasta",
        null=True,
        blank=True,
        help_text="Fecha hasta la cual está vigente la garantía"
    )
    ubicacion = models.CharField(
        max_length=200,
        verbose_name="Ubicación",
        blank=True,
        help_text="Ubicación física del equipo"
    )
    observaciones = models.TextField(
        verbose_name="Observaciones",
        blank=True,
        help_text="Notas adicionales sobre el equipo"
    )
    
    cantidad_equipo = models.PositiveIntegerField(
        verbose_name="Cantidad de Equipos",
        null=True,
        blank=True,
        help_text="Cantidad de equipos"
    )

    descripcion = models.TextField(
        verbose_name="Descripción",
        blank=True,
        help_text="Descripción detallada del equipo"
    )
    imagen = models.ImageField(
        verbose_name="Imagen del equipo",
        upload_to="equipos_audio/",
        blank=True,
        null=True,
        help_text="Imagen del equipo de audio"
    )
    
    class Meta:
        verbose_name = "Equipo de Audio"
        verbose_name_plural = "Equipos de Audio"
        ordering = ['nombre', 'marca', 'modelo']
        indexes = [
            models.Index(fields=['tipo', 'estado']),
            models.Index(fields=['marca', 'modelo']),
        ]
    
    def __str__(self):
        if self.nombre:
            return self.nombre
        elif self.marca and self.modelo:
            return f"{self.marca} {self.modelo}"
        else:
            return f"Equipo {self.id}"
    
    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del equipo"""
        parts = []
        if self.marca:
            parts.append(self.marca)
        if self.modelo:
            parts.append(self.modelo)
        if self.nombre and self.nombre not in ' '.join(parts):
            parts.insert(0, self.nombre)
        return ' '.join(parts) if parts else f"Equipo {self.id}"
    
    @property
    def esta_disponible(self):
        """Indica si el equipo está disponible para uso"""
        return self.estado == 'disponible' and self.is_active
    
    @property
    def necesita_mantenimiento(self):
        """Indica si el equipo necesita mantenimiento"""
        return self.estado in ['mantenimiento', 'averiado']
    
    def marcar_en_uso(self):
        """Marca el equipo como en uso"""
        if self.esta_disponible:
            self.estado = 'en_uso'
            self.save()
            return True
        return False
    
    def marcar_disponible(self):
        """Marca el equipo como disponible"""
        if self.estado == 'en_uso':
            self.estado = 'disponible'
            self.save()
            return True
        return False
