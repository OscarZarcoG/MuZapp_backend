from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, time
from core.models import BaseModel
from ..CLIENTS.models import Client


class ContractManager(models.Manager):
    """Manager personalizado para Contract"""
    
    def pending(self):
        """Contratos pendientes"""
        return self.filter(estado_evento='pending')
    
    def confirmed(self):
        """Contratos confirmados"""
        return self.filter(estado_evento='confirmed')
    
    def in_progress(self):
        """Contratos en progreso"""
        return self.filter(estado_evento='in_progress')
    
    def completed(self):
        """Contratos completados"""
        return self.filter(estado_evento='completed')
    
    def cancelled(self):
        """Contratos cancelados"""
        return self.filter(estado_evento='cancelled')
    
    def by_date_range(self, start_date, end_date):
        """Contratos en un rango de fechas"""
        return self.filter(
            fecha_evento__gte=start_date,
            fecha_evento__lte=end_date
        )
    
    def by_client(self, cliente_id):
        """Contratos por cliente"""
        return self.filter(cliente_id=cliente_id)
    
    def upcoming(self):
        """Contratos próximos (fecha futura)"""
        return self.filter(fecha_evento__gte=timezone.now().date())
    
    def past(self):
        """Contratos pasados"""
        return self.filter(fecha_evento__lt=timezone.now().date())


class Contract(BaseModel):
    """Modelo para contratos de eventos musicales"""
    
    # Choices para estado del evento
    ESTADO_EVENTO_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Choices para tipo de evento
    TIPO_EVENTO_CHOICES = [
        ('birthday', 'Cumpleaños'),
        ('wedding', 'Boda'),
        ('quinceañera', 'Quinceañera'),
        ('baptism', 'Bautizo'),
        ('communion', 'Comunión'),
        ('graduation', 'Graduación'),
        ('anniversary', 'Aniversario'),
        ('corporate', 'Corporativo'),
        ('baby_shower', 'Baby Shower'),
        ('bridal_shower', 'Despedida de Soltera'),
        ('christmas', 'Navidad'),
        ('new_year', 'Año Nuevo'),
        ('other', 'Otro'),
    ]
    
    # Manager personalizado
    objects = ContractManager()
    
    # Información básica
    numero_contrato = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número único del contrato"
    )
    estado_evento = models.CharField(
        max_length=20,
        choices=ESTADO_EVENTO_CHOICES,
        default='pending',
        help_text="Estado actual del evento"
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Título descriptivo del evento"
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        help_text="Tipo de evento a realizar"
    )
    nombre_festejado = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre de la persona festejada (si aplica)"
    )
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre el evento"
    )
    
    # Fecha y hora
    fecha_evento = models.DateField(
        help_text="Fecha del evento"
    )
    hora_inicio = models.TimeField(
        help_text="Hora de inicio del evento"
    )
    hora_final = models.TimeField(
        help_text="Hora de finalización del evento"
    )
    tiempo_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duración total en minutos (calculado automáticamente)"
    )
    
    # Descansos
    oportunidades_descanso = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(10)],
        help_text="Número de descansos programados"
    )
    tiempo_descanso = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(120)],
        help_text="Duración de cada descanso en minutos"
    )
    descripcion_descanso = models.TextField(
        blank=True,
        help_text="Descripción de los descansos"
    )
    
    # Lugar
    nombre_lugar = models.CharField(
        max_length=200,
        help_text="Nombre del lugar del evento"
    )
    descripcion_lugar = models.TextField(
        blank=True,
        help_text="Descripción detallada del lugar"
    )
    google_maps_url = models.URLField(
        blank=True,
        help_text="URL de Google Maps del lugar"
    )
    fotos_lugar = models.ImageField(
        upload_to='contratos/lugares/',
        null=True,
        blank=True,
        help_text="Fotos del lugar del evento"
    )
    
    # Información financiera
    pago_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monto total del contrato"
    )
    costo_hora = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Costo por hora del servicio"
    )
    pago_adelanto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monto del adelanto recibido"
    )
    pago_restante = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monto restante por cobrar (calculado automáticamente)"
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Porcentaje del adelanto sobre el total"
    )
    costo_extra = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Costos adicionales"
    )
    
    # Relaciones
    cliente = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='contratos',
        help_text="Cliente que contrata el servicio"
    )
    audiencia = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número estimado de personas en el evento"
    )
    
    # Relaciones opcionales con otras subapps
    equipo_audio = models.ForeignKey(
        'AUDIO.AudioEquipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos',
        help_text="Equipo de audio asignado"
    )
    catering = models.ForeignKey(
        'CATERING.Catering',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos',
        help_text="Servicio de catering asociado"
    )
    
    # Relación many-to-many con peticiones de clientes
    peticiones_cliente = models.ManyToManyField(
        'CLIENTS_REQUESTS.ClientRequest',
        blank=True,
        related_name='contratos',
        help_text="Peticiones musicales del cliente"
    )
    
    class Meta:
        db_table = 'gigs_contract'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-fecha_evento', '-created_at']
        indexes = [
            models.Index(fields=['numero_contrato']),
            models.Index(fields=['estado_evento']),
            models.Index(fields=['fecha_evento']),
            models.Index(fields=['cliente']),
            models.Index(fields=['tipo_evento']),
            models.Index(fields=['-fecha_evento', 'estado_evento']),
        ]
    
    def __str__(self):
        return f"{self.numero_contrato} - {self.titulo} ({self.fecha_evento})"
    
    def save(self, *args, **kwargs):
        """Override save para generar número de contrato y calcular campos"""
        if not self.numero_contrato:
            self.numero_contrato = self.generate_contract_number()
        
        # Calcular tiempo total
        if self.hora_inicio and self.hora_final:
            self.tiempo_total = self.calculate_total_time()
        
        # Calcular pago restante y porcentaje
        self.calculate_payment_fields()
        
        super().save(*args, **kwargs)
    
    def generate_contract_number(self):
        """Genera un número único de contrato"""
        from datetime import datetime
        year = datetime.now().year
        
        # Obtener el último número de contrato del año
        last_contract = Contract.objects.filter(
            numero_contrato__startswith=f'CT-{year}'
        ).order_by('-numero_contrato').first()
        
        if last_contract:
            try:
                last_number = int(last_contract.numero_contrato.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f'CT-{year}-{new_number:04d}'
    
    def calculate_total_time(self):
        """Calcula el tiempo total en minutos"""
        if not self.hora_inicio or not self.hora_final:
            return None
        
        # Convertir a datetime para calcular diferencia
        inicio = datetime.combine(self.fecha_evento, self.hora_inicio)
        final = datetime.combine(self.fecha_evento, self.hora_final)
        
        # Si la hora final es menor que la inicial, asumimos que es al día siguiente
        if final <= inicio:
            from datetime import timedelta
            final += timedelta(days=1)
        
        diferencia = final - inicio
        return int(diferencia.total_seconds() / 60)
    
    def calculate_payment_fields(self):
        """Calcula campos de pago automáticamente"""
        if self.pago_total and self.pago_adelanto:
            self.pago_restante = self.pago_total - self.pago_adelanto
            
            if self.pago_total > 0:
                self.porcentaje = (self.pago_adelanto / self.pago_total) * 100
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que la fecha del evento no sea en el pasado (solo para nuevos contratos)
        if not self.pk and self.fecha_evento and self.fecha_evento < timezone.now().date():
            raise ValidationError({
                'fecha_evento': 'La fecha del evento no puede ser en el pasado.'
            })
        
        # Validar que la hora final sea posterior a la inicial
        if self.hora_inicio and self.hora_final:
            if self.hora_final <= self.hora_inicio:
                # Permitir si es al día siguiente (diferencia mayor a 12 horas)
                inicio_minutes = self.hora_inicio.hour * 60 + self.hora_inicio.minute
                final_minutes = self.hora_final.hour * 60 + self.hora_final.minute
                
                if final_minutes + (24 * 60) - inicio_minutes < 60:  # Menos de 1 hora
                    raise ValidationError({
                        'hora_final': 'La hora final debe ser posterior a la hora de inicio.'
                    })
        
        # Validar que el adelanto no sea mayor al total
        if self.pago_total and self.pago_adelanto and self.pago_adelanto > self.pago_total:
            raise ValidationError({
                'pago_adelanto': 'El adelanto no puede ser mayor al pago total.'
            })
        
        # Validar conflictos de horario
        self.validate_schedule_conflict()
    
    def validate_schedule_conflict(self):
        """Valida conflictos de horario con otros contratos"""
        if not self.fecha_evento or not self.hora_inicio or not self.hora_final:
            return
        
        # Buscar contratos en la misma fecha que no estén cancelados
        conflicting_contracts = Contract.objects.filter(
            fecha_evento=self.fecha_evento,
            estado_evento__in=['confirmed', 'in_progress']
        ).exclude(pk=self.pk if self.pk else None)
        
        for contract in conflicting_contracts:
            if self.times_overlap(contract):
                raise ValidationError({
                    'hora_inicio': f'Conflicto de horario con el contrato {contract.numero_contrato}'
                })
    
    def times_overlap(self, other_contract):
        """Verifica si hay solapamiento de horarios con otro contrato"""
        return (
            self.hora_inicio < other_contract.hora_final and
            self.hora_final > other_contract.hora_inicio
        )
    
    # Métodos de estado
    def esta_pendiente(self):
        """Verifica si el contrato está pendiente"""
        return self.estado_evento == 'pending'
    
    def esta_confirmado(self):
        """Verifica si el contrato está confirmado"""
        return self.estado_evento == 'confirmed'
    
    def esta_en_progreso(self):
        """Verifica si el contrato está en progreso"""
        return self.estado_evento == 'in_progress'
    
    def esta_completado(self):
        """Verifica si el contrato está completado"""
        return self.estado_evento == 'completed'
    
    def esta_cancelado(self):
        """Verifica si el contrato está cancelado"""
        return self.estado_evento == 'cancelled'
    
    def puede_cancelar(self):
        """Verifica si el contrato puede ser cancelado"""
        return self.estado_evento in ['pending', 'confirmed']
    
    def puede_confirmar(self):
        """Verifica si el contrato puede ser confirmado"""
        return self.estado_evento == 'pending'
    
    def puede_iniciar(self):
        """Verifica si el contrato puede iniciarse"""
        return self.estado_evento == 'confirmed'
    
    def puede_completar(self):
        """Verifica si el contrato puede completarse"""
        return self.estado_evento == 'in_progress'
    
    # Métodos de cambio de estado
    def confirmar(self, notas_confirmacion=''):
        """Confirma el contrato"""
        if not self.puede_confirmar():
            raise ValidationError('El contrato no puede ser confirmado en su estado actual.')
        
        self.estado_evento = 'confirmed'
        if notas_confirmacion:
            self.notas = f"{self.notas}\n\nConfirmado: {notas_confirmacion}" if self.notas else f"Confirmado: {notas_confirmacion}"
        self.save()
    
    def iniciar(self):
        """Inicia el contrato (marca como en progreso)"""
        if not self.puede_iniciar():
            raise ValidationError('El contrato no puede iniciarse en su estado actual.')
        
        self.estado_evento = 'in_progress'
        self.save()
    
    def completar(self, notas_finalizacion=''):
        """Completa el contrato"""
        if not self.puede_completar():
            raise ValidationError('El contrato no puede completarse en su estado actual.')
        
        self.estado_evento = 'completed'
        if notas_finalizacion:
            self.notas = f"{self.notas}\n\nCompletado: {notas_finalizacion}" if self.notas else f"Completado: {notas_finalizacion}"
        self.save()
    
    def cancelar(self, motivo_cancelacion):
        """Cancela el contrato"""
        if not self.puede_cancelar():
            raise ValidationError('El contrato no puede ser cancelado en su estado actual.')
        
        self.estado_evento = 'cancelled'
        self.notas = f"{self.notas}\n\nCancelado: {motivo_cancelacion}" if self.notas else f"Cancelado: {motivo_cancelacion}"
        self.save()
    
    # Métodos de cálculo
    def dias_hasta_evento(self):
        """Calcula días hasta el evento"""
        if not self.fecha_evento:
            return None
        
        diferencia = self.fecha_evento - timezone.now().date()
        return diferencia.days
    
    def horas_totales(self):
        """Calcula las horas totales del evento"""
        if self.tiempo_total:
            return round(self.tiempo_total / 60, 2)
        return None
    
    def porcentaje_adelanto(self):
        """Calcula el porcentaje del adelanto"""
        if self.pago_total and self.pago_adelanto and self.pago_total > 0:
            return round((self.pago_adelanto / self.pago_total) * 100, 2)
        return 0
    
    def costo_por_persona(self):
        """Calcula el costo por persona"""
        if self.pago_total and self.audiencia and self.audiencia > 0:
            return round(self.pago_total / self.audiencia, 2)
        return None
    
    # Propiedades calculadas
    @property
    def duracion_horas(self):
        """Duración en horas como propiedad"""
        return self.horas_totales()
    
    @property
    def esta_proximo(self):
        """Verifica si el evento está próximo (en los próximos 7 días)"""
        dias = self.dias_hasta_evento()
        return dias is not None and 0 <= dias <= 7
    
    @property
    def esta_vencido(self):
        """Verifica si el evento ya pasó"""
        dias = self.dias_hasta_evento()
        return dias is not None and dias < 0
