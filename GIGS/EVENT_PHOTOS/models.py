from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from PIL import Image
import os
from ..models import BaseModel
from ..CONTRACT.models import Contract
from ..CLIENTS.models import Client


class EventPhotoManager(models.Manager):
    """Manager personalizado para EventPhoto"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def public_photos(self):
        """Fotos públicas"""
        return self.get_queryset().filter(publicas=True)
    
    def featured_photos(self):
        """Fotos destacadas"""
        return self.get_queryset().filter(destacadas=True)
    
    def by_event(self, evento_nombre):
        """Fotos por nombre de evento"""
        return self.get_queryset().filter(evento__icontains=evento_nombre)
    
    def by_client(self, cliente_id):
        """Fotos por cliente"""
        return self.get_queryset().filter(cliente_id=cliente_id)
    
    def by_contract(self, contract_id):
        """Fotos por contrato"""
        return self.get_queryset().filter(contrato_id=contract_id)
    
    def by_date_range(self, start_date, end_date):
        """Fotos en un rango de fechas"""
        return self.get_queryset().filter(
            fecha_evento__gte=start_date,
            fecha_evento__lte=end_date
        )
    
    def by_photographer(self, fotografo):
        """Fotos por fotógrafo"""
        return self.get_queryset().filter(fotografo__icontains=fotografo)
    
    def recent(self, days=30):
        """Fotos recientes"""
        from datetime import timedelta
        cutoff_date = timezone.now().date() - timedelta(days=days)
        return self.get_queryset().filter(created_at__date__gte=cutoff_date)


def event_photo_upload_path(instance, filename):
    """Generar ruta de subida para fotos de eventos"""
    # Crear estructura: event_photos/YYYY/MM/evento_nombre/filename
    fecha = instance.fecha_evento or timezone.now().date()
    evento_slug = instance.evento.replace(' ', '_').lower() if instance.evento else 'sin_evento'
    return f'event_photos/{fecha.year}/{fecha.month:02d}/{evento_slug}/{filename}'


class EventPhoto(BaseModel):
    """Modelo para fotos de eventos"""
    
    TIPO_EVENTO_CHOICES = [
        ('birthday', 'Cumpleaños'),
        ('wedding', 'Boda'),
        ('quinceañera', 'Quinceañera'),
        ('baptism', 'Bautizo'),
        ('communion', 'Primera Comunión'),
        ('graduation', 'Graduación'),
        ('anniversary', 'Aniversario'),
        ('corporate', 'Evento Corporativo'),
        ('baby_shower', 'Baby Shower'),
        ('bridal_shower', 'Despedida de Soltera'),
        ('christmas', 'Navidad'),
        ('new_year', 'Año Nuevo'),
        ('concert', 'Concierto'),
        ('otros', 'Otros'),
    ]
    
    # Información básica de la foto
    nombre_foto = models.CharField(
        max_length=255,
        help_text="Nombre descriptivo de la foto"
    )
    
    foto = models.ImageField(
        upload_to=event_photo_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp']
            )
        ],
        help_text="Archivo de imagen (JPG, PNG, WEBP)"
    )
    
    fecha_foto = models.DateField(
        help_text="Fecha en que se tomó la foto"
    )
    
    # Información del evento
    evento = models.CharField(
        max_length=255,
        help_text="Nombre del evento"
    )
    
    fecha_evento = models.DateField(
        help_text="Fecha del evento"
    )
    
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        default='otros',
        help_text="Tipo de evento"
    )
    
    ubicacion = models.CharField(
        max_length=255,
        blank=True,
        help_text="Ubicación donde se tomó la foto"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción de la foto o momento capturado"
    )
    
    # Información del fotógrafo
    fotografo = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombre del fotógrafo"
    )
    
    # Configuración de visibilidad
    publicas = models.BooleanField(
        default=True,
        help_text="Si la foto es visible en la galería pública"
    )
    
    destacadas = models.BooleanField(
        default=False,
        help_text="Si la foto aparece en la sección destacadas"
    )
    
    # Relaciones opcionales
    cliente = models.ForeignKey(
        'CLIENTS.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fotos_eventos',
        help_text="Cliente asociado al evento"
    )
    
    contrato = models.ForeignKey(
        'CONTRACT.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fotos_evento',
        help_text="Contrato asociado al evento"
    )
    
    # Metadatos de la imagen (se calculan automáticamente)
    ancho_imagen = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Ancho de la imagen en píxeles"
    )
    
    alto_imagen = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Alto de la imagen en píxeles"
    )
    
    tamaño_archivo = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Tamaño del archivo en bytes"
    )
    
    # Manager personalizado
    objects = EventPhotoManager()
    
    class Meta:
        db_table = 'event_photos'
        verbose_name = 'Foto de Evento'
        verbose_name_plural = 'Fotos de Eventos'
        ordering = ['-fecha_evento', '-fecha_foto', '-created_at']
        indexes = [
            models.Index(fields=['fecha_evento']),
            models.Index(fields=['fecha_foto']),
            models.Index(fields=['evento']),
            models.Index(fields=['tipo_evento']),
            models.Index(fields=['publicas']),
            models.Index(fields=['destacadas']),
            models.Index(fields=['cliente']),
            models.Index(fields=['contrato']),
            models.Index(fields=['fotografo']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.nombre_foto} - {self.evento} ({self.fecha_evento})"
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para calcular metadatos de imagen"""
        # Si es una nueva foto o se cambió la imagen
        if self.foto and (not self.pk or 'foto' in kwargs.get('update_fields', [])):
            self._calculate_image_metadata()
        
        super().save(*args, **kwargs)
    
    def _calculate_image_metadata(self):
        """Calcular metadatos de la imagen"""
        try:
            if self.foto and hasattr(self.foto, 'file'):
                # Obtener dimensiones
                with Image.open(self.foto.file) as img:
                    self.ancho_imagen, self.alto_imagen = img.size
                
                # Obtener tamaño del archivo
                self.foto.file.seek(0, os.SEEK_END)
                self.tamaño_archivo = self.foto.file.tell()
                self.foto.file.seek(0)
        except Exception:
            # Si hay error, mantener valores nulos
            pass
    
    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        errors = {}
        
        # Validar que fecha_foto no sea futura
        if self.fecha_foto and self.fecha_foto > timezone.now().date():
            errors['fecha_foto'] = 'La fecha de la foto no puede ser futura.'
        
        # Validar que fecha_evento no sea muy antigua (más de 10 años)
        if self.fecha_evento:
            from datetime import timedelta
            limite_antiguo = timezone.now().date() - timedelta(days=365*10)
            if self.fecha_evento < limite_antiguo:
                errors['fecha_evento'] = 'La fecha del evento no puede ser anterior a 10 años.'
        
        # Validar que fecha_foto no sea anterior a fecha_evento (con margen de 1 día)
        if self.fecha_foto and self.fecha_evento:
            from datetime import timedelta
            if self.fecha_foto < self.fecha_evento - timedelta(days=1):
                errors['fecha_foto'] = 'La fecha de la foto no puede ser anterior al evento.'
        
        # Validar nombre de evento
        if self.evento and len(self.evento.strip()) < 3:
            errors['evento'] = 'El nombre del evento debe tener al menos 3 caracteres.'
        
        if errors:
            raise ValidationError(errors)
    
    # Propiedades calculadas
    @property
    def tamaño_archivo_mb(self):
        """Tamaño del archivo en MB"""
        if self.tamaño_archivo:
            return round(self.tamaño_archivo / (1024 * 1024), 2)
        return 0
    
    @property
    def resolucion(self):
        """Resolución de la imagen como string"""
        if self.ancho_imagen and self.alto_imagen:
            return f"{self.ancho_imagen}x{self.alto_imagen}"
        return "Desconocida"
    
    @property
    def es_horizontal(self):
        """True si la imagen es horizontal"""
        if self.ancho_imagen and self.alto_imagen:
            return self.ancho_imagen > self.alto_imagen
        return None
    
    @property
    def es_cuadrada(self):
        """True si la imagen es cuadrada"""
        if self.ancho_imagen and self.alto_imagen:
            return self.ancho_imagen == self.alto_imagen
        return None
    
    @property
    def dias_desde_evento(self):
        """Días transcurridos desde el evento"""
        if self.fecha_evento:
            delta = timezone.now().date() - self.fecha_evento
            return delta.days
        return None
    
    @property
    def url_foto(self):
        """URL de la foto"""
        if self.foto:
            return self.foto.url
        return None
    
    # Métodos de utilidad
    def marcar_como_destacada(self):
        """Marcar foto como destacada"""
        self.destacadas = True
        self.save(update_fields=['destacadas', 'updated_at'])
    
    def quitar_destacada(self):
        """Quitar foto de destacadas"""
        self.destacadas = False
        self.save(update_fields=['destacadas', 'updated_at'])
    
    def hacer_publica(self):
        """Hacer foto pública"""
        self.publicas = True
        self.save(update_fields=['publicas', 'updated_at'])
    
    def hacer_privada(self):
        """Hacer foto privada"""
        self.publicas = False
        self.save(update_fields=['publicas', 'updated_at'])
    
    def delete(self, using=None, keep_parents=False):
        """Sobrescribir delete para eliminar archivo físico"""
        # Eliminar archivo físico
        if self.foto:
            try:
                if os.path.isfile(self.foto.path):
                    os.remove(self.foto.path)
            except Exception:
                pass
        
        super().delete(using=using, keep_parents=keep_parents)
