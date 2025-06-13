# GIGS/models.py
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

"""  B A S E   M O D E L   """
class BaseModel(models.Model):
    is_active = models.BooleanField(
        default=True,
        verbose_name="Estado"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de borrado"
    )
    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.deleted_at = models.DateTimeField(auto_now_add=True)
        self.save()

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()

    def is_deleted(self):
        return self.deleted_at is not None

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


""" C L I E N T E S """
class Cliente(BaseModel):
    nombre_cliente = models.CharField(
        max_length=255,
        verbose_name="Nombre del cliente",
        default="Cliente"
    )
    telefono_cliente = models.CharField(
        max_length=255,
        verbose_name="Teléfono del cliente",
        default="Teléfono"
    )
    redes_sociales = models.URLField(
        verbose_name="Redes sociales",
        default="Redes sociales",
        blank=True
    )
    frecuencia = models.PositiveIntegerField(
        verbose_name="Frecuencia"
    )
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    def __str__(self):
        return f"{self.nombre_cliente}"


""" A U D I O """
class Equipo_Audio(BaseModel):
    marca = models.CharField(
        max_length=200,
        verbose_name="Marca"
    )
    modelo = models.CharField(
        max_length=200,
        verbose_name="Modelo"
    )
    numero_bocinas = models.PositiveIntegerField(
        verbose_name="Número de bocinas"
    )

    descripcion = models.TextField(
        verbose_name="Descripción"
    )
    precio = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    class Meta:
        verbose_name = "Equipo de audio"
        verbose_name_plural = "Equipos de audio"
    def __str__(self):
        return f"{self.marca} {self.modelo}"


""" C A T E R I N G """
class Catering(BaseModel):
    peticion_grupo = models.TextField(
        verbose_name="Petición del grupo"
    )
    
    class Meta:
        verbose_name = "Catering"
        verbose_name_plural = "Caterings"
    def __str__(self):    
        return f"{self.peticion_grupo}"


""" P E T I C I O N E S """
class Peticion(BaseModel):
    nombre_cancion = models.CharField(
        max_length=255,
        verbose_name="Nombre de la canción"
    )
    link = models.URLField(
        verbose_name="Link",
        blank=True,
        null=True
    )
    class Meta:
        verbose_name = "Petición"
        verbose_name_plural = "Peticiones"
    def __str__(self):
        return f"{self.nombre_cancion}"


""" R E P E R T O R I O """
class Repertorio(BaseModel):
    nombre_cancion = models.CharField(
        max_length=255,
        verbose_name="Nombre de la canción"
    ) # Debe permitir agregar canciones
    class Meta:
        verbose_name = "Repertorio"
        verbose_name_plural = "Repertorios"
    def __str__(self):
        return f"{self.nombre_cancion}"


""" F O T O S   E V E N T O """
class Fotos_Evento(BaseModel):
    nombre_foto = models.CharField(
        max_length=255,
        verbose_name="Nombre de la foto"
    )
    fecha_foto = models.DateField(
        verbose_name="Fecha de la foto"
    )
    foto = models.ImageField(
        upload_to='fotos_evento/',
        verbose_name="Foto",
    )
    class Meta:
        verbose_name = "Foto del evento"
        verbose_name_plural = "Fotos del evento"
    def __str__(self):
        return f"{self.nombre_foto}"
    

""" C O N T R A T O """
class Contrato(BaseModel):
    PERSONAS_CHOICES = [(i, f'{i} personas') for i in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250, 300]]

    STATUS_EVENTO_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]

    TIPO_EVENTO_CHOICES = [
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

    OPORTUNIDADES_DESCANSO_CHOICES = [(i, str(i)) for i in range(1, 6)]

    TIEMPO_DESCANSO_CHOICES = [
        (10, '10 minutos'), (15, '15 minutos'), (20, '20 minutos'),
        (30, '30 minutos'), (45, '45 minutos'), (60, '1 hora'),
    ]

    # Información básica
    numero_contrato = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de contrato",
        editable=False,
        blank=True
    ) # Se genera automáticamente con el formato YYYYMMDD-NNN (YYYY = Año, MM = Mes, DD = Día, NNN = Número de contrato - comeinza con 0001)
    estado_evento = models.CharField(
        max_length=255,
        choices=STATUS_EVENTO_CHOICES,
        verbose_name="Estado del evento",
        default="Pendiente"
    )# SE SUPONE QUE DEBE ESTAR CAMBIANDO DE ACUERDO A LAS HORAS Y FECHAS QUE SE EJECUTA, ADEMÁS DEBE CAMBIAR SI YA HUBO UN DEPÓSITO PARA CONFIRMAR SU EVENTO
    # No ha dado adelanto ni confirmado = Pendiente
    # Dió adelanto el cliente = Confirmado
    # El día y la hora del evento = En progreso
    # El evento ha finalizado = Completado
    # El evento ha sido cancelado = Cancelado
    titulo = models.CharField(
        max_length=255,
        verbose_name="Título del evento",
        default="Evento"
    )
    tipo_evento = models.CharField(
        max_length=255,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de evento",
        default="Cumpleaños"
    )
    nombre_festejado = models.CharField(
        max_length=255,
        verbose_name="Nombre del festejado",
        default="Festejado"
    )
    notas = models.TextField(
        verbose_name="Notas",
        default="Notas",
        blank=True,
        help_text="¿Necesita alguna nota especial?"
    )
    fecha_evento = models.DateField(
        verbose_name="Fecha del evento",
        db_index=True
    )
    hora_inicio = models.TimeField(
        verbose_name="Hora de inicio"
    )
    hora_final = models.TimeField(
        verbose_name="Hora de finalización"
    )
    tiempo_total = models.PositiveIntegerField(
        verbose_name="Horas totales del evento",
        editable=False,
        null=True, blank=True,
        help_text="Se calcula automáticamente"
    ) # SE DEBE CALCULAR AUTOMATICAMENTE CON LA HORA DE INICIO Y FINAL
    # Ejemplo:  Hora de inicio: 10:00, Hora de finalización: 13:00, Tiempo total: 3 horas
    
    
    
    # Descansos
    oportunidades_descanso = models.PositiveIntegerField(
        verbose_name="Oportunidades de descanso",
        choices=OPORTUNIDADES_DESCANSO_CHOICES,
        blank=True,
        null=True
    )
    tiempo_descanso = models.PositiveIntegerField(
        verbose_name="Tiempo de descanso",
        choices=TIEMPO_DESCANSO_CHOICES,
        blank=True,
        null=True
    )
    descripcion_descanso = models.TextField(
        verbose_name="Descripción del descanso",
        default="Descripción",
        blank=True,
        null=True
    )


    # Lugar
    nombre_lugar = models.CharField(
        max_length=255,
        verbose_name="Nombre del lugar",
        default="Lugar"
    )
    descripcion_lugar = models.TextField(
        verbose_name="Descripción del lugar",
        default="Descripción",
        blank=True
    )
    google_maps_url = models.URLField(
        verbose_name="URL Google Maps"
    )
    fotos_lugar = models.ImageField(
        upload_to='lugar_fotos/',
        verbose_name="Fotos del lugar",
        blank=True,
        null=True
    )


    # Información financiera
    pago_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total",
        default=0,
        help_text="Se calcula automáticamente"
    ) # Se calcula automáticamente con el costo por hora, el adelanto dado y el tiempo total
    # Ejemplo:  Costo por hora: $1000, Adelanto: $500, Tiempo total: 3 horas, Total: $2500
    costo_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Costo por hora",
        default=0
    )
    pago_adelanto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Adelanto",
        default=0
    )
    pago_restante = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Restante",
        default=0
    ) # Se calcula automáticamente con el costo por hora, el adelanto dado y el tiempo total
    # Ejemplo:  Costo por hora: $1000, Adelanto: $500, Tiempo total: 3 horas, Restante: $1000
    porcentaje = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Porcentaje pagado",
        default=0
    ) # Se calcula automáticamente con el costo por hora, el adelanto dado y el tiempo total
    # Ejemplo:  Costo por hora: $1000, Adelanto: $500, Tiempo total: 3 horas, Porcentaje pagado: 50%
    costo_extra = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Costo extra",
        default=0
    ) # En caso de solicitar más tiempo al estipulado en el contrato se cobrará un costo extra (un poco menor a la cantidad del costo por hora)
    # Ejemplo:  Costo por hora: $1000, Tiempo total: 3 horas, Costo extra: $800, Total: $1800

    # Cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente"
    ) # Debe de permitir elegir un cliente o crear uno nuevo al momento


    # Audiencia
    audiencia = models.IntegerField(
        choices=PERSONAS_CHOICES,
        verbose_name="Audiencia",
        default=10
    )


    # Audio
    equipo_audio = models.ForeignKey(
        Equipo_Audio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Equipo de audio"
    )
    
    
    # Requerimientos
    catering = models.ForeignKey(
        Catering,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catering"
    ) # Debe de permitir elegir un catering o crear uno nuevo al momento
    peticiones_cliente = models.ManyToManyField(
        Peticion,
        verbose_name="Peticiones del cliente",
        blank=True
    ) # Se pueden agregar peticiones al momento de crear el contrato
    
    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-fecha_evento']
    
    def save(self, *args, **kwargs):
        # Generar número de contrato automáticamente
        if not self.numero_contrato:
            self.numero_contrato = self.generar_numero_contrato()
        
        # Calcular tiempo total
        if self.hora_inicio and self.hora_final:
            self.tiempo_total = self.calcular_tiempo_total()
        
        # Calcular valores financieros
        if self.costo_hora and self.tiempo_total:
            self.pago_total = self.calcular_pago_total()
            self.pago_restante = self.calcular_pago_restante()
            self.porcentaje = self.calcular_porcentaje()
        
        # Actualizar estado del evento
        self.actualizar_estado_evento()
        
        super().save(*args, **kwargs)
    
    def generar_numero_contrato(self):
        """Genera número de contrato con formato YYYYMMDD-NNN"""
        from django.utils import timezone
        fecha_hoy = timezone.now().date()
        fecha_str = fecha_hoy.strftime('%Y%m%d')
        
        # Buscar el último contrato del día
        ultimo_contrato = Contrato.objects.filter(
            numero_contrato__startswith=fecha_str
        ).order_by('-numero_contrato').first()
        
        if ultimo_contrato:
            ultimo_numero = int(ultimo_contrato.numero_contrato.split('-')[1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        return f"{fecha_str}-{nuevo_numero:04d}"
    
    def calcular_tiempo_total(self):
        """Calcula el tiempo total del evento en horas"""
        if not self.hora_inicio or not self.hora_final:
            return 0
        
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        final = datetime.combine(datetime.today(), self.hora_final)
        
        # Si la hora final es menor que la inicial, asumimos que es al día siguiente
        if final < inicio:
            final += timedelta(days=1)
        
        diferencia = final - inicio
        return int(diferencia.total_seconds() / 3600)  # Convertir a horas
    
    def calcular_pago_total(self):
        """Calcula el pago total del evento"""
        if not self.costo_hora or not self.tiempo_total:
            return 0
        return (self.costo_hora * self.tiempo_total) + self.costo_extra
    
    def calcular_pago_restante(self):
        """Calcula el pago restante del evento"""
        return self.pago_total - self.pago_adelanto
    
    def calcular_porcentaje(self):
        """Calcula el porcentaje pagado del evento"""
        if not self.pago_total or self.pago_total == 0:
            return 0
        return (self.pago_adelanto / self.pago_total) * 100
    
    def actualizar_estado_evento(self):
        """Actualiza el estado del evento según las condiciones"""
        from django.utils import timezone
        ahora = timezone.now()
        fecha_evento_datetime = datetime.combine(self.fecha_evento, self.hora_inicio)
        fecha_final_datetime = datetime.combine(self.fecha_evento, self.hora_final)
        
        # Si la hora final es menor que la inicial, el evento termina al día siguiente
        if self.hora_final < self.hora_inicio:
            fecha_final_datetime += timedelta(days=1)
        
        # Lógica de estados
        if self.estado_evento == 'cancelled':
            return  # No cambiar si está cancelado
        
        if self.pago_adelanto > 0 and ahora.date() < self.fecha_evento:
            self.estado_evento = 'confirmed'
        elif ahora.date() == self.fecha_evento and ahora.time() >= self.hora_inicio and ahora.time() <= self.hora_final:
            self.estado_evento = 'in_progress'
        elif ahora > fecha_final_datetime.replace(tzinfo=timezone.get_current_timezone()):
            self.estado_evento = 'completed'
        elif self.pago_adelanto == 0:
            self.estado_evento = 'pending'
    
    def generar_contrato_pdf(self):
        """Genera el contrato en formato PDF"""
        # Esta función se implementará con la librería de generación de documentos
        pass
    
    def generar_contrato_docx(self):
        """Genera el contrato en formato DOCX"""
        # Esta función se implementará con la librería de generación de documentos
        pass
    
    def __str__(self):
        return f"Contrato {self.numero_contrato} - {self.titulo}"