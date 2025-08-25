from django.db import models
from django.core.validators import URLValidator
from core.models import BaseModel


class ClientRequestManager(models.Manager):
    """Manager personalizado para ClientRequest"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def pending(self):
        """Retorna peticiones pendientes"""
        return self.get_queryset().filter(estado='pendiente')
    
    def approved(self):
        """Retorna peticiones aprobadas"""
        return self.get_queryset().filter(estado='aprobada')
    
    def rejected(self):
        """Retorna peticiones rechazadas"""
        return self.get_queryset().filter(estado='rechazada')
    
    def by_client(self, cliente_id):
        """Retorna peticiones de un cliente específico"""
        return self.get_queryset().filter(cliente_id=cliente_id)


class ClientRequest(BaseModel):
    """Modelo para las peticiones de canciones de los clientes"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('en_repertorio', 'En Repertorio'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Información de la canción
    nombre_cancion = models.CharField(
        max_length=255,
        verbose_name="Nombre de la canción",
        help_text="Título de la canción solicitada"
    )
    artista = models.CharField(
        max_length=255,
        verbose_name="Artista",
        blank=True,
        help_text="Nombre del artista o banda"
    )
    album = models.CharField(
        max_length=255,
        verbose_name="Álbum",
        blank=True,
        help_text="Nombre del álbum"
    )
    genero = models.CharField(
        max_length=100,
        verbose_name="Género musical",
        blank=True,
        help_text="Género musical de la canción"
    )
    
    # Enlaces y referencias
    link = models.URLField(
        verbose_name="Enlace",
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Enlace a YouTube, Spotify, etc."
    )
    link_partitura = models.URLField(
        verbose_name="Enlace a partitura",
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Enlace a la partitura o acordes"
    )
    
    # Información del cliente y evento
    cliente = models.ForeignKey(
        'CLIENTS.Client',
        on_delete=models.CASCADE,
        verbose_name="Cliente",
        help_text="Cliente que solicita la canción"
    )
    evento_relacionado = models.ForeignKey(
        'GIGS.Contrato',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Evento relacionado",
        help_text="Contrato/evento para el cual se solicita la canción"
    )
    
    # Estado y prioridad
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado",
        help_text="Estado actual de la petición"
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name="Prioridad",
        help_text="Prioridad de la petición"
    )
    
    # Fechas importantes
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de solicitud",
        help_text="Fecha en que se realizó la petición"
    )
    fecha_necesaria = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha necesaria",
        help_text="Fecha para cuando se necesita la canción"
    )
    fecha_respuesta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de respuesta",
        help_text="Fecha en que se respondió a la petición"
    )
    
    # Notas y observaciones
    notas_cliente = models.TextField(
        blank=True,
        verbose_name="Notas del cliente",
        help_text="Comentarios o notas adicionales del cliente"
    )
    notas_internas = models.TextField(
        blank=True,
        verbose_name="Notas internas",
        help_text="Notas internas para el músico/banda"
    )
    motivo_rechazo = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
        help_text="Razón por la cual se rechazó la petición"
    )
    
    # Información técnica
    dificultad_estimada = models.CharField(
        max_length=20,
        choices=[
            ('facil', 'Fácil'),
            ('intermedio', 'Intermedio'),
            ('dificil', 'Difícil'),
            ('muy_dificil', 'Muy Difícil'),
        ],
        blank=True,
        verbose_name="Dificultad estimada",
        help_text="Dificultad estimada para aprender la canción"
    )
    tiempo_estimado_aprendizaje = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo estimado (horas)",
        help_text="Horas estimadas para aprender la canción"
    )
    
    # Manager personalizado
    objects = ClientRequestManager()
    
    class Meta:
        verbose_name = "Petición de Cliente"
        verbose_name_plural = "Peticiones de Clientes"
        ordering = ['-fecha_solicitud', '-prioridad']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
            models.Index(fields=['cliente']),
            models.Index(fields=['fecha_solicitud']),
            models.Index(fields=['fecha_necesaria']),
        ]
    
    def __str__(self):
        return f"{self.nombre_cancion} - {self.cliente.nombre_completo}"
    
    @property
    def nombre_completo_cancion(self):
        """Retorna el nombre completo de la canción con artista"""
        if self.artista:
            return f"{self.nombre_cancion} - {self.artista}"
        return self.nombre_cancion
    
    @property
    def esta_pendiente(self):
        """Verifica si la petición está pendiente"""
        return self.estado == 'pendiente'
    
    @property
    def esta_aprobada(self):
        """Verifica si la petición está aprobada"""
        return self.estado == 'aprobada'
    
    @property
    def esta_rechazada(self):
        """Verifica si la petición está rechazada"""
        return self.estado == 'rechazada'
    
    @property
    def es_urgente(self):
        """Verifica si la petición es urgente"""
        return self.prioridad == 'urgente'
    
    @property
    def dias_hasta_fecha_necesaria(self):
        """Calcula los días hasta la fecha necesaria"""
        if self.fecha_necesaria:
            from datetime import date
            delta = self.fecha_necesaria - date.today()
            return delta.days
        return None
    
    def aprobar(self, notas_internas=None):
        """Aprueba la petición"""
        self.estado = 'aprobada'
        if notas_internas:
            self.notas_internas = notas_internas
        from django.utils import timezone
        self.fecha_respuesta = timezone.now()
        self.save()
    
    def rechazar(self, motivo):
        """Rechaza la petición"""
        self.estado = 'rechazada'
        self.motivo_rechazo = motivo
        from django.utils import timezone
        self.fecha_respuesta = timezone.now()
        self.save()
    
    def marcar_en_repertorio(self):
        """Marca la petición como agregada al repertorio"""
        self.estado = 'en_repertorio'
        self.save()
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que si está rechazada, tenga motivo
        if self.estado == 'rechazada' and not self.motivo_rechazo:
            raise ValidationError({
                'motivo_rechazo': 'Debe especificar un motivo para rechazar la petición.'
            })
        
        # Validar fecha necesaria
        if self.fecha_necesaria:
            from datetime import date
            if self.fecha_necesaria < date.today():
                raise ValidationError({
                    'fecha_necesaria': 'La fecha necesaria no puede ser anterior a hoy.'
                })
