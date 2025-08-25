# GIGS/CATERING/models.py
from django.db import models
from core.models import BaseModel, BaseModelManager

class CateringManager(BaseModelManager):
    def active_requests(self):
        return self.filter(is_active=True)
    
    def by_group(self, grupo):
        return self.filter(peticion_grupo__icontains=grupo, is_active=True)

class Catering(BaseModel):
    objects = CateringManager()
    
    peticion_grupo = models.TextField(
        verbose_name="Petición del Grupo",
        help_text="Descripción detallada de la petición de catering del grupo musical",
        blank=True
    )
    
    # Campos adicionales para mejorar la funcionalidad
    tipo_evento = models.CharField(
        max_length=100,
        verbose_name="Tipo de Evento",
        blank=True,
        help_text="Tipo de evento para el cual se solicita el catering"
    )
    
    numero_personas = models.PositiveIntegerField(
        verbose_name="Número de Personas",
        null=True,
        blank=True,
        help_text="Número estimado de personas para el catering"
    )
    
    presupuesto_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Presupuesto Estimado",
        null=True,
        blank=True,
        help_text="Presupuesto estimado para el catering"
    )
    
    fecha_evento = models.DateTimeField(
        verbose_name="Fecha del Evento",
        null=True,
        blank=True,
        help_text="Fecha y hora del evento"
    )
    
    ubicacion = models.CharField(
        max_length=200,
        verbose_name="Ubicación",
        blank=True,
        help_text="Ubicación donde se realizará el evento"
    )
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('confirmado', 'Confirmado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado",
        db_index=True
    )
    
    proveedor = models.CharField(
        max_length=200,
        verbose_name="Proveedor",
        blank=True,
        help_text="Nombre del proveedor de catering seleccionado"
    )
    
    contacto_proveedor = models.CharField(
        max_length=200,
        verbose_name="Contacto del Proveedor",
        blank=True,
        help_text="Información de contacto del proveedor"
    )
    
    notas_adicionales = models.TextField(
        verbose_name="Notas Adicionales",
        blank=True,
        help_text="Notas adicionales sobre el catering"
    )
    
    class Meta:
        verbose_name = "Catering"
        verbose_name_plural = "Catering"
        ordering = ['-fecha_evento', '-created_at']
        indexes = [
            models.Index(fields=['estado', 'fecha_evento']),
            models.Index(fields=['proveedor']),
        ]
    
    def __str__(self):
        if self.tipo_evento:
            return f"Catering - {self.tipo_evento}"
        elif self.fecha_evento:
            return f"Catering - {self.fecha_evento.strftime('%d/%m/%Y')}"
        else:
            return f"Catering {self.id}"
    
    @property
    def esta_pendiente(self):
        """Indica si la solicitud de catering está pendiente"""
        return self.estado == 'pendiente'
    
    @property
    def esta_confirmado(self):
        """Indica si la solicitud de catering está confirmada"""
        return self.estado == 'confirmado'
    
    @property
    def puede_cancelar(self):
        """Indica si la solicitud puede ser cancelada"""
        return self.estado in ['pendiente', 'en_proceso']
    
    def confirmar(self):
        """Confirma la solicitud de catering"""
        if self.estado in ['pendiente', 'en_proceso']:
            self.estado = 'confirmado'
            self.save()
            return True
        return False
    
    def cancelar(self):
        """Cancela la solicitud de catering"""
        if self.puede_cancelar:
            self.estado = 'cancelado'
            self.save()
            return True
        return False
    
    def completar(self):
        """Marca la solicitud como completada"""
        if self.estado == 'confirmado':
            self.estado = 'completado'
            self.save()
            return True
        return False
