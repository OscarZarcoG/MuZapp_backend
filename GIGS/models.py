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
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
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
    
    redes_sociales = models.URLField(
        verbose_name="Redes sociales",
        blank=True,
        help_text="Enlaces a redes sociales del cliente"
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


""" A U D I O """
class Equipo_Audio(BaseModel):
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
        default="Equipo sin nombre"
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_EQUIPO_CHOICES,
        default='altavoces',
        verbose_name="Tipo de Equipo"
    )
    marca = models.CharField(
        max_length=200,
        verbose_name="Marca",
        blank=True
    )
    modelo = models.CharField(
        max_length=200,
        verbose_name="Modelo",
        blank=True
    )
    numero_serie = models.CharField(
        max_length=200,
        verbose_name="Número de Serie",
        blank=True
    )
    estado = models.CharField(
        max_length=50,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name="Estado"
    )
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Compra",
        null=True,
        blank=True
    )
    fecha_compra = models.DateField(
        verbose_name="Fecha de Compra",
        null=True,
        blank=True
    )
    garantia_hasta = models.DateField(
        verbose_name="Garantía Hasta",
        null=True,
        blank=True
    )
    ubicacion = models.CharField(
        max_length=200,
        verbose_name="Ubicación",
        blank=True
    )
    observaciones = models.TextField(
        verbose_name="Observaciones",
        blank=True
    )
    
    # Campos legacy para compatibilidad
    numero_bocinas = models.PositiveIntegerField(
        verbose_name="Número de bocinas",
        null=True,
        blank=True
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        blank=True
    )
    imagen = models.ImageField(
        verbose_name="Imagen del equipo",
        upload_to="equipos_audio/",
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = "Equipo de audio"
        verbose_name_plural = "Equipos de audio"
        ordering = ['nombre', 'marca', 'modelo']
    
    def __str__(self):
        if self.nombre:
            return self.nombre
        elif self.marca and self.modelo:
            return f"{self.marca} {self.modelo}"
        else:
            return f"Equipo {self.id}"


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
        default="pending"
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
        default="birthday"
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
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar que la hora de inicio sea anterior a la hora final (excepto eventos que cruzan medianoche)
        if self.hora_inicio and self.hora_final:
            # Permitir eventos que cruzan medianoche (ej: 20:00 a 02:00)
            if self.hora_inicio == self.hora_final:
                raise ValidationError({
                    'hora_final': 'La hora de finalización debe ser diferente a la hora de inicio.'
                })
        
        # Validar conflictos de horarios
        if self.fecha_evento and self.hora_inicio and self.hora_final:
            try:
                self.validar_conflictos_horarios()
            except ValidationError as e:
                raise ValidationError({
                    'fecha_evento': str(e)
                })
    
    def save(self, *args, **kwargs):
        # Ejecutar validaciones del modelo
        self.full_clean()
        
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
        
        # Actualizar estado del evento basado en adelantos
        self.actualizar_estado_evento()
        
        super().save(*args, **kwargs)
    
    def generar_numero_contrato(self):
        """Genera número de contrato con formato YYYYMMDD-NNN con numeración secuencial global"""
        if not self.fecha_evento:
            from django.utils import timezone
            fecha_base = timezone.now().date()
        else:
            fecha_base = self.fecha_evento
            
        fecha_str = fecha_base.strftime('%Y%m%d')
        
        # Buscar el último contrato de todos los contratos para obtener el número secuencial más alto
        ultimo_contrato = Contrato.objects.exclude(
            numero_contrato__isnull=True
        ).exclude(
            numero_contrato=''
        ).order_by('-id').first()
        
        if ultimo_contrato and ultimo_contrato.numero_contrato:
            try:
                ultimo_numero = int(ultimo_contrato.numero_contrato.split('-')[1])
                nuevo_numero = ultimo_numero + 1
            except (IndexError, ValueError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        return f"{fecha_str}-{nuevo_numero:04d}"
    
    def validar_conflictos_horarios(self):
        """Valida que no haya conflictos de horarios en el mismo día con separación mínima de 1 hora"""
        from django.core.exceptions import ValidationError
        from datetime import datetime, timedelta
        
        # Buscar otros contratos en la misma fecha
        contratos_mismo_dia = Contrato.objects.filter(
            fecha_evento=self.fecha_evento,
            estado_evento__in=['confirmed', 'pending', 'in_progress']
        ).exclude(id=self.id if self.id else None)
        
        inicio_actual = datetime.combine(self.fecha_evento, self.hora_inicio)
        final_actual = datetime.combine(self.fecha_evento, self.hora_final)
        
        # Si la hora final es menor que la inicial, el evento termina al día siguiente
        if self.hora_final < self.hora_inicio:
            final_actual += timedelta(days=1)
        
        for contrato in contratos_mismo_dia:
            inicio_existente = datetime.combine(contrato.fecha_evento, contrato.hora_inicio)
            final_existente = datetime.combine(contrato.fecha_evento, contrato.hora_final)
            
            # Si la hora final es menor que la inicial, el evento termina al día siguiente
            if contrato.hora_final < contrato.hora_inicio:
                final_existente += timedelta(days=1)
            
            # Verificar si hay solapamiento o falta de separación mínima
            # Los eventos se solapan si: inicio_actual < final_existente AND final_actual > inicio_existente
            hay_solapamiento = inicio_actual < final_existente and final_actual > inicio_existente
            
            if hay_solapamiento:
                raise ValidationError(
                    f"Conflicto de horarios: Ya existe un evento el {self.fecha_evento} "
                    f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                    f"Los eventos no pueden solaparse."
                )
            
            # Verificar separación mínima de 1 hora entre eventos
            # Si el nuevo evento es después del existente
            if inicio_actual >= final_existente:
                diferencia = (inicio_actual - final_existente).total_seconds() / 3600
                if diferencia < 1:
                    raise ValidationError(
                        f"Conflicto de horarios: Ya existe un evento el {self.fecha_evento} "
                        f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                        f"Debe haber al menos 1 hora de diferencia entre eventos."
                    )
            
            # Si el nuevo evento es antes del existente
            elif final_actual <= inicio_existente:
                diferencia = (inicio_existente - final_actual).total_seconds() / 3600
                if diferencia < 1:
                    raise ValidationError(
                        f"Conflicto de horarios: Ya existe un evento el {self.fecha_evento} "
                        f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                        f"Debe haber al menos 1 hora de diferencia entre eventos."
                    )
    
    def calcular_tiempo_total(self):
        """Calcula el tiempo total del evento en horas con redondeo hacia arriba después de 45 minutos"""
        if not self.hora_inicio or not self.hora_final:
            return 0
        
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        final = datetime.combine(datetime.today(), self.hora_final)
        
        # Si la hora final es menor que la inicial, asumimos que es al día siguiente
        if final < inicio:
            final += timedelta(days=1)
        
        diferencia = final - inicio
        total_segundos = diferencia.total_seconds()
        horas_exactas = total_segundos / 3600
        
        # Redondear hacia arriba si los minutos son >= 45
        horas_enteras = int(horas_exactas)
        minutos_restantes = (horas_exactas - horas_enteras) * 60
        
        if minutos_restantes >= 45:
            return horas_enteras + 1
        else:
            return horas_enteras if horas_enteras > 0 else 1  # Mínimo 1 hora
    
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
        """Actualiza el estado del evento según las condiciones basadas en adelantos y fechas"""
        from django.utils import timezone
        ahora = timezone.now()
        fecha_evento_datetime = datetime.combine(self.fecha_evento, self.hora_inicio)
        fecha_final_datetime = datetime.combine(self.fecha_evento, self.hora_final)
        
        # Si la hora final es menor que la inicial, el evento termina al día siguiente
        if self.hora_final < self.hora_inicio:
            fecha_final_datetime += timedelta(days=1)
        
        # Lógica de estados mejorada
        if self.estado_evento == 'cancelled':
            return  # No cambiar si está cancelado
        
        # Verificar si el evento ya terminó
        if ahora > fecha_final_datetime.replace(tzinfo=timezone.get_current_timezone()):
            self.estado_evento = 'completed'
        # Verificar si el evento está en progreso
        elif (ahora.date() == self.fecha_evento and 
              ahora.time() >= self.hora_inicio and 
              ahora.time() <= self.hora_final) or \
             (self.hora_final < self.hora_inicio and 
              ahora.date() == self.fecha_evento and 
              ahora.time() >= self.hora_inicio) or \
             (self.hora_final < self.hora_inicio and 
              ahora.date() == self.fecha_evento + timedelta(days=1) and 
              ahora.time() <= self.hora_final):
            self.estado_evento = 'in_progress'
        # Verificar si hay adelanto para confirmar
        elif self.pago_adelanto > 0:
            self.estado_evento = 'confirmed'
        # Sin adelanto, queda pendiente
        else:
            self.estado_evento = 'pending'
    
    def generar_contrato_pdf(self):
        """Genera el contrato en formato PDF usando ReportLab (rápido)"""
        from .pdf_generator import generar_contrato_pdf_reportlab
        return generar_contrato_pdf_reportlab(self)
    
    def generar_contrato_docx(self):
        """Genera el contrato en formato DOCX"""
        from .utils import generar_contrato_docx
        return generar_contrato_docx(self)
    
    def __str__(self):
        return f"Contrato {self.numero_contrato} - {self.titulo}"