# models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal


class BaseTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        abstract = True


class BookingEvent(BaseTimeStampedModel):
    AUDIENCE_CHOICES = [(i, f'{i} personas') for i in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250, 300]]

    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('under_review', 'En revisión'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('contract_generated', 'Contrato Generado'),
        ('signed', 'Firmado'),
    ]

    EVENT_TYPE_CHOICES = [
        ('birthday', 'Cumpleaños'),
        ('wedding', 'Boda'),
        ('quinceañera', 'XV Años'),
        ('baptism', 'Bautizo'),
        ('communion', 'Primera Comunión'),
        ('graduation', 'Graduación'),
        ('anniversary', 'Aniversario'),
        ('corporate', 'Evento Corporativo'),
        ('baby_shower', 'Baby Shower'),
        ('bridal_shower', 'Despedida de Soltera'),
        ('christmas', 'Navidad'),
        ('new_year', 'Año Nuevo'),
        ('other', 'Otro'),
    ]

    BREAK_OPPORTUNITY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    BREAK_TIME_CHOICES = [
        (10, '10 minutos'), (15, '15 minutos'), (20, '20 minutos'),
        (30, '30 minutos'), (45, '45 minutos'), (60, '1 hora'),
    ]

    # Identificación única del contrato
    contract_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de contrato",
        editable=False,
        blank=True
    )

    # Información básica
    title = models.CharField(max_length=200, verbose_name="Título del evento", db_index=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name="Tipo de evento", db_index=True)
    celebrant_name = models.CharField(max_length=200, verbose_name="Nombre del festejado", blank=True)
    description = models.TextField(blank=True, verbose_name="Descripción/Notas del evento")
    date = models.DateField(verbose_name="Fecha del evento", db_index=True)
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de finalización")
    tiempo_total = models.PositiveIntegerField(
        verbose_name="Tiempo total del evento (minutos)",
        editable=False,
        null=True, blank=True,
        help_text="Se calcula automáticamente"
    )

    # Información adicional
    break_opportunity = models.PositiveIntegerField(choices=BREAK_OPPORTUNITY_CHOICES, verbose_name="Oportunidades de descanso")
    break_times = models.PositiveIntegerField(choices=BREAK_TIME_CHOICES, verbose_name="Duración de cada descanso")

    # Lugar
    venue_name = models.CharField(max_length=200, verbose_name="Nombre del lugar")
    venue_description = models.TextField(blank=True, verbose_name="Descripción del lugar")
    venue_dimensions = models.CharField(max_length=200, blank=True, verbose_name="Dimensiones del lugar")
    venue_capacity = models.PositiveIntegerField(verbose_name="Capacidad para personas del lugar")
    google_maps_url = models.URLField(blank=True, verbose_name="URL Google Maps")
    waze_url = models.URLField(blank=True, verbose_name="URL Waze")

    # Información financiera (Solo admins pueden modificar)
    advance_payment = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Adelanto",
        default=0
    )

    total_payment = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total",
        default=0,
        help_text="Se calcula automáticamente"
    )

    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        verbose_name="Tarifa por hora"
    )

    # Datos de contacto del cliente
    client_name = models.CharField(max_length=200, verbose_name="Nombre del cliente")
    client_phone = models.CharField(max_length=20, verbose_name="Teléfono del cliente")
    client_social_media = models.URLField(blank=True, verbose_name="Red social del cliente")

    # Audiencia y requerimientos
    expected_audience = models.IntegerField(choices=AUDIENCE_CHOICES, verbose_name="Personas esperadas")
    audio_description = models.TextField(blank=True, verbose_name="Descripción técnica del audio")
    backstage_requirements = models.TextField(blank=True, verbose_name="Requerimientos backstage")
    client_song_requests = models.TextField(blank=True, verbose_name="Peticiones de canciones")
    song_links = models.TextField(blank=True, verbose_name="Enlaces de YouTube (uno por línea)")
    additional_notes = models.TextField(blank=True, verbose_name="Notas adicionales")

    # Metadatos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado",  db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por", related_name="events_created")
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Asignado a",
        related_name="events_assigned",
        limit_choices_to={'groups__name': 'Grupo_nort'}
    )

    # Campos para el contrato
    contract_terms = models.TextField(
        blank=True,
        verbose_name="Términos y condiciones específicos",
        help_text="Términos adicionales para este contrato específico"
    )
    contract_file = models.FileField(
        upload_to='contracts/%Y/%m/',
        blank=True, null=True,
        verbose_name="Archivo de contrato"
    )
    contract_generated_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Contrato generado el"
    )

    class Meta:
        verbose_name = "Evento/Contrato Digital"
        verbose_name_plural = "Eventos/Contratos Digitales"
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['created_by', 'date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['contract_number']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(advance_payment__lte=models.F('total_payment')),
                name='advance_not_greater_than_total'
            ),
        ]

    def save(self, *args, **kwargs):
        # 1. Generar número de contrato único si no existe
        if not self.contract_number:
            self.contract_number = self.generate_contract_number()

        # 2. Calcular tiempo total automáticamente
        if self.start_time and self.end_time:
            self.tiempo_total = self.calculate_duration_minutes()

        # 3. Calcular total automáticamente si es necesario
        if self.should_calculate_total():
            self.total_payment = self.calculate_total_from_hourly()

        # 4. Ejecutar validaciones completas
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_contract_number(self):
        """Genera número único de contrato"""
        year = datetime.now().year
        # Obtener el último número del año
        last_contract = BookingEvent.objects.filter(
            contract_number__startswith=f"GN{year}"
        ).order_by('-contract_number').first()

        if last_contract:
            try:
                last_num = int(last_contract.contract_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1

        return f"GN{year}-{new_num:04d}"

    def calculate_duration_minutes(self):
        """Calcula la duración del evento en minutos"""
        if not (self.start_time and self.end_time):
            return 0

        start_dt = datetime.combine(self.date or datetime.today().date(), self.start_time)
        end_dt = datetime.combine(self.date or datetime.today().date(), self.end_time)

        # Manejar eventos que terminan al día siguiente
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        duration_seconds = (end_dt - start_dt).total_seconds()
        return int(duration_seconds / 60)  # Convertir a minutos

    def __str__(self):
        celebrant_info = f" - {self.celebrant_name}" if self.celebrant_name else ""
        return f"{self.contract_number}: {self.title}{celebrant_info} - {self.date}"

    def clean(self):
        errors = {}

        # Validar horarios
        if self.start_time and self.end_time:
            if self.start_time == self.end_time:
                errors['end_time'] = "La hora de fin debe ser diferente a la de inicio"

        # Validar pagos
        if self.advance_payment and self.total_payment:
            if self.advance_payment > self.total_payment:
                errors['advance_payment'] = "El adelanto no puede ser mayor al total"

        # Validar conflictos de horario solo para eventos confirmados
        if self.status in ['confirmed', 'in_progress']:
            try:
                self._validate_schedule_conflicts()
            except ValidationError as e:
                errors['date'] = e.message

        if errors:
            raise ValidationError(errors)

    def _validate_schedule_conflicts(self):
        """Valida que no haya conflictos de horario"""
        if not all([self.date, self.start_time, self.end_time]):
            return

        # Calcular el rango de tiempo con buffer de 2 horas
        event_start = datetime.combine(self.date, self.start_time)
        event_end = datetime.combine(self.date, self.end_time)

        # Si el evento termina al día siguiente
        if self.end_time <= self.start_time:
            event_end += timedelta(days=1)

        # Buffer de 2 horas antes y después
        buffer_start = event_start - timedelta(hours=2)
        buffer_end = event_end + timedelta(hours=2)

        # Buscar eventos conflictivos confirmados
        conflicting_events = BookingEvent.objects.filter(
            date=self.date,
            status__in=['confirmed', 'in_progress', 'contract_generated', 'signed']
        )

        # Excluir el evento actual si ya existe
        if self.pk:
            conflicting_events = conflicting_events.exclude(pk=self.pk)

        for event in conflicting_events:
            other_start = datetime.combine(event.date, event.start_time)
            other_end = datetime.combine(event.date, event.end_time)

            # Si el otro evento termina al día siguiente
            if event.end_time <= event.start_time:
                other_end += timedelta(days=1)

            # Verificar solapamiento considerando el buffer
            if not (buffer_end <= other_start or buffer_start >= other_end):
                raise ValidationError(
                    f"Conflicto de horario con el evento '{event.title}' "
                    f"({event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}). "
                    f"Debe haber al menos 2 horas entre eventos."
                )

    def should_calculate_total(self):
        """Verifica si debe calcular el total automáticamente"""
        return (
                self.start_time and
                self.end_time and
                self.hourly_rate and
                self.hourly_rate > 0 and
                (not self.total_payment or self.total_payment == Decimal('0'))
        )

    def calculate_total_from_hourly(self):
        """Calcula el total basado en la tarifa por hora"""
        if not self.hourly_rate or self.hourly_rate <= 0:
            return Decimal('0')

        duration = self.duration_hours
        if duration <= 0:
            return Decimal('0')

        return self.hourly_rate * Decimal(str(duration))

    @property
    def duration_hours(self):
        """Duración del evento en horas"""
        if not (self.start_time and self.end_time):
            return 0

        start_dt = datetime.combine(self.date or datetime.today().date(), self.start_time)
        end_dt = datetime.combine(self.date or datetime.today().date(), self.end_time)

        # Manejar eventos que terminan al día siguiente
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        duration_seconds = (end_dt - start_dt).total_seconds()
        return round(duration_seconds / 3600, 2)

    @property
    def total_break_minutes(self):
        """Total de minutos de descanso calculado"""
        if not self.break_opportunity or not self.break_times:
            return 0
        return self.break_opportunity * self.break_times

    @property
    def pending_payment(self):
        """Monto pendiente de pago"""
        total = self.total_payment or Decimal('0')
        advance = self.advance_payment or Decimal('0')
        return max(total - advance, Decimal('0'))

    @property
    def is_upcoming(self):
        """Verifica si el evento es futuro"""
        if not self.date:
            return False
        return self.date >= datetime.now().date()

    @property
    def is_today(self):
        """Verifica si el evento es hoy"""
        if not self.date:
            return False
        return self.date == datetime.now().date()

    @property
    def payment_percentage(self):
        """Porcentaje de pago completado"""
        if not self.total_payment or self.total_payment == 0:
            return 0
        advance = self.advance_payment or Decimal('0')
        return float((advance / self.total_payment) * 100)

    @property
    def can_edit(self):
        """Verifica si puede ser editado"""
        return self.status in ['draft', 'pending', 'under_review']

    @property
    def can_generate_contract(self):
        """Verifica si se puede generar contrato"""
        return self.status == 'confirmed' and not self.contract_file

    def get_song_links_list(self):
        """Lista de enlaces de YouTube"""
        if not self.song_links:
            return []
        return [link.strip() for link in self.song_links.split('\n') if link.strip()]

    def add_song_link(self, url):
        """Agrega enlace de YouTube"""
        current_links = self.song_links.strip() if self.song_links else ""
        if current_links:
            self.song_links = f"{current_links}\n{url.strip()}"
        else:
            self.song_links = url.strip()

    def remove_song_link(self, url):
        """Remueve enlace específico"""
        if not self.song_links:
            return
        links = self.get_song_links_list()
        links = [link for link in links if link != url.strip()]
        self.song_links = '\n'.join(links)

    def get_formatted_duration(self):
        """Retorna la duración formateada"""
        if self.tiempo_total:
            hours = self.tiempo_total // 60
            minutes = self.tiempo_total % 60

            if hours == 0:
                return f"{minutes} min"
            elif minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {minutes}min"

        # Fallback al método anterior si tiempo_total no está calculado
        hours = self.duration_hours
        if hours == 0:
            return "No definida"

        whole_hours = int(hours)
        minutes = int((hours - whole_hours) * 60)

        if minutes == 0:
            return f"{whole_hours}h"
        else:
            return f"{whole_hours}h {minutes}min"


class ContractSignature(BaseTimeStampedModel):
    """Firmas digitales del contrato"""
    SIGNATURE_TYPE_CHOICES = [
        ('client', 'Cliente'),
        ('grupo_nort', 'Grupo Nort'),
    ]

    event = models.ForeignKey(
        BookingEvent,
        on_delete=models.CASCADE,
        related_name='signatures',
        verbose_name="Evento"
    )
    signature_type = models.CharField(
        max_length=20,
        choices=SIGNATURE_TYPE_CHOICES,
        verbose_name="Tipo de firma"
    )
    signed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Firmado por"
    )
    signature_data = models.TextField(
        verbose_name="Datos de la firma",
        help_text="Datos base64 de la firma digital"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Dirección IP"
    )
    signed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Firmado el"
    )

    class Meta:
        verbose_name = "Firma de contrato"
        verbose_name_plural = "Firmas de contratos"
        unique_together = ['event', 'signature_type']
        ordering = ['-signed_at']

    def __str__(self):
        return f"Firma {self.get_signature_type_display()} - {self.event.contract_number}"


class EventPhoto(BaseTimeStampedModel):
    """Fotos del evento"""
    event = models.ForeignKey(
        BookingEvent,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Evento"
    )
    image = models.ImageField(
        upload_to='event_photos/%Y/%m/',
        verbose_name="Foto"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Foto destacada"
    )

    class Meta:
        verbose_name = "Foto del evento"
        verbose_name_plural = "Fotos del evento"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"Foto de {self.event.title} - {self.created_at.strftime('%d/%m/%Y')}"


class VenueTemplate(models.Model):
    """Plantillas de lugares frecuentes"""
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        unique=True
    )
    address = models.TextField(verbose_name="Dirección")
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    dimensions = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Dimensiones"
    )
    capacity = models.PositiveIntegerField(verbose_name="Capacidad")
    google_maps_url = models.URLField(
        blank=True,
        verbose_name="Google Maps"
    )
    waze_url = models.URLField(
        blank=True,
        verbose_name="Waze"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        verbose_name = "Plantilla de lugar"
        verbose_name_plural = "Plantillas de lugares"
        ordering = ['name']

    def __str__(self):
        return self.name


class AudioTemplate(models.Model):
    """Plantillas de configuraciones de audio"""
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        unique=True
    )
    description = models.TextField(verbose_name="Descripción técnica")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        verbose_name = "Plantilla de audio"
        verbose_name_plural = "Plantillas de audio"
        ordering = ['name']

    def __str__(self):
        return self.name


class ContractTemplate(models.Model):
    """Plantillas de contratos"""
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        unique=True
    )
    content = models.TextField(
        verbose_name="Contenido del contrato",
        help_text="Use variables como {{client_name}}, {{event_date}}, {{total_payment}}, etc."
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Plantilla por defecto"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de contrato"
        verbose_name_plural = "Plantillas de contratos"
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} {'(Por defecto)' if self.is_default else ''}"

    def save(self, *args, **kwargs):
        # Asegurar que solo haya una plantilla por defecto
        if self.is_default:
            ContractTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)