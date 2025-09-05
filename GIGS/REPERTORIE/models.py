from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re
from ..models import BaseModel


class RepertorioManager(models.Manager):
    """Manager personalizado para el modelo Repertorio"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def por_genero(self, genero):
        """Obtiene canciones por género"""
        return self.filter(genero__icontains=genero)
    
    def por_artista(self, artista):
        """Obtiene canciones por artista"""
        return self.filter(artista__icontains=artista)
    
    def por_duracion(self, min_duracion=None, max_duracion=None):
        """Filtra canciones por rango de duración"""
        queryset = self.get_queryset()
        if min_duracion:
            queryset = queryset.filter(duracion_segundos__gte=min_duracion)
        if max_duracion:
            queryset = queryset.filter(duracion_segundos__lte=max_duracion)
        return queryset
    
    def buscar(self, termino):
        """Búsqueda general en nombre de canción y artista"""
        return self.filter(
            models.Q(nombre_cancion__icontains=termino) |
            models.Q(artista__icontains=termino)
        )
    
    def con_link(self):
        """Obtiene canciones que tienen link"""
        return self.filter(link__isnull=False).exclude(link='')
    
    def sin_link(self):
        """Obtiene canciones que no tienen link"""
        return self.filter(models.Q(link__isnull=True) | models.Q(link=''))
    
    def recientes(self, dias=30):
        """Obtiene canciones agregadas recientemente"""
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(created_at__gte=fecha_limite)
    
    def populares(self):
        """Obtiene canciones más populares (ordenadas por uso en contratos)"""
        # Esto requeriría una relación con contratos, por ahora ordenamos por fecha
        return self.order_by('-created_at')


class Generos(BaseModel):
    objects = RepertorioManager()
    GENEROS_CHOICES = [
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('jazz', 'Jazz'),
        ('blues', 'Blues'),
        ('country', 'Country'),
        ('folk', 'Folk'),
        ('reggae', 'Reggae'),
        ('hip_hop', 'Hip Hop'),
        ('electronic', 'Electrónica'),
        ('classical', 'Clásica'),
        ('latin', 'Latina'),
        ('salsa', 'Salsa'),
        ('merengue', 'Merengue'),
        ('bachata', 'Bachata'),
        ('cumbia', 'Cumbia'),
        ('vallenato', 'Vallenato'),
        ('ranchera', 'Ranchera'),
        ('mariachi', 'Mariachi'),
        ('bolero', 'Bolero'),
        ('tango', 'Tango'),
        ('bossa_nova', 'Bossa Nova'),
        ('reggaeton', 'Reggaetón'),
        ('trap', 'Trap'),
        ('funk', 'Funk'),
        ('soul', 'Soul'),
        ('r_and_b', 'R&B'),
        ('gospel', 'Gospel'),
        ('indie', 'Indie'),
        ('alternative', 'Alternativo'),
        ('punk', 'Punk'),
        ('metal', 'Metal'),
        ('disco', 'Disco'),
        ('house', 'House'),
        ('techno', 'Techno'),
        ('ambient', 'Ambient'),
        ('instrumental', 'Instrumental'),
        ('otros', 'Otros'),
    ]
    nombre = models.CharField(
        max_length=255,
        verbose_name="Nombre",
        help_text="Nombre del género"
    )
    def __str__(self):
        return self.nombre

class Repertorio(BaseModel):      
    DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('intermedio', 'Intermedio'),
        ('dificil', 'Difícil'),
        ('experto', 'Experto'),
    ]
    
    nombre_cancion = models.CharField(
        max_length=200,
        verbose_name='Nombre de la canción',
        help_text='Título de la canción'
    )
    artista = models.CharField(
        max_length=200,
        verbose_name='Artista',
        help_text='Nombre del artista o banda'
    )
    genero = models.ForeignKey(
        Generos,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Género',
        help_text='Género musical de la canción'
    )
    duracion = models.CharField(
        max_length=10,
        verbose_name='Duración',
        help_text='Duración en formato MM:SS o HH:MM:SS',
        blank=True,
        null=True
    )
    duracion_segundos = models.PositiveIntegerField(
        verbose_name='Duración en segundos',
        help_text='Duración total en segundos (calculado automáticamente)',
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(7200)]
    )
    dificultad = models.CharField(
        max_length=20,
        choices=DIFICULTAD_CHOICES,
        default='intermedio',
        verbose_name='Dificultad',
        help_text='Nivel de dificultad para tocar la canción'
    )
    tonalidad = models.CharField(
        max_length=10,
        verbose_name='Tonalidad',
        help_text='Tonalidad de la canción (ej: C, Am, F#)',
        blank=True,
        null=True
    )
    tempo = models.PositiveIntegerField(
        verbose_name='Tempo (BPM)',
        help_text='Tempo en beats por minuto',
        null=True,
        blank=True,
        validators=[MinValueValidator(40), MaxValueValidator(300)]
    )
    progresion_acordes = models.TextField(
        verbose_name='Acordes',
        help_text='Acordes utilizados en la canción',
        blank=True,
        null=True
    )    
    letra = models.TextField(
        verbose_name='Letra',
        help_text='Letra de la canción',
        blank=True,
        null=True
    )
    pista_audio = models.FileField(
        upload_to='pistas_audio/',
        verbose_name='Pista de audio',
        help_text='Pista de audio de la canción',
        blank=True,
        null=True
    )
    link = models.URLField(
        verbose_name='Enlace',
        help_text='Enlace a YouTube, Spotify, etc.',
        blank=True,
        null=True
    )
    
    link_partitura = models.URLField(
        verbose_name='Enlace a partitura',
        help_text='Enlace a la partitura o acordes',
        blank=True,
        null=True
    )
    
    notas = models.TextField(
        verbose_name='Notas',
        help_text='Notas adicionales sobre la canción',
        blank=True,
        null=True
    )
    
    veces_tocada = models.PositiveIntegerField(
        default=0,
        verbose_name='Veces tocada',
        help_text='Número de veces que se ha tocado esta canción'
    )
    
    ultima_vez_tocada = models.DateTimeField(
        verbose_name='Última vez tocada',
        help_text='Fecha de la última vez que se tocó',
        null=True,
        blank=True
    )
    
    etiquetas = models.CharField(
        max_length=500,
        verbose_name='Etiquetas',
        help_text='Etiquetas separadas por comas (ej: bailable, romántica, navideña)',
        blank=True,
        null=True
    )
    
    es_favorita = models.BooleanField(
        default=False,
        verbose_name='Es favorita',
        help_text='Marcar como canción favorita'
    )
    
    objects = RepertorioManager()
    
    class Meta:
        verbose_name = 'Canción del Repertorio'
        verbose_name_plural = 'Repertorio Musical'
        ordering = ['nombre_cancion', 'artista']
        indexes = [
            models.Index(fields=['nombre_cancion']),
            models.Index(fields=['artista']),
            models.Index(fields=['genero']),
            models.Index(fields=['dificultad']),
            models.Index(fields=['es_favorita']),
            models.Index(fields=['veces_tocada']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['nombre_cancion', 'artista']
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular la duración en segundos"""
        if self.duracion:
            self.duracion_segundos = self._calcular_duracion_segundos()
        super().save(*args, **kwargs)
    
    def _calcular_duracion_segundos(self):
        """Convierte la duración en formato MM:SS o HH:MM:SS a segundos"""
        if not self.duracion:
            return None
        
        try:
            duracion_limpia = self.duracion.strip()
            
            partes = duracion_limpia.split(':')
            
            if len(partes) == 2:  # MM:SS
                minutos, segundos = map(int, partes)
                return minutos * 60 + segundos
            elif len(partes) == 3:  # HH:MM:SS
                horas, minutos, segundos = map(int, partes)
                return horas * 3600 + minutos * 60 + segundos
            else:
                return None
        except (ValueError, AttributeError):
            return None
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        if self.duracion:
            patron_duracion = re.compile(r'^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$')
            if not patron_duracion.match(self.duracion.strip()):
                raise ValidationError({
                    'duracion': 'Formato inválido. Use MM:SS o HH:MM:SS'
                })
        
        if self.tonalidad:
            patron_tonalidad = re.compile(r'^[A-G][#b]?[m]?$')
            if not patron_tonalidad.match(self.tonalidad.strip()):
                raise ValidationError({
                    'tonalidad': 'Formato inválido. Ejemplos: C, Am, F#, Bb'
                })
    
    def __str__(self):
        return f"{self.nombre_cancion} - {self.artista}"
    
    @property
    def duracion_formateada(self):
        """Devuelve la duración en formato legible"""
        if not self.duracion_segundos:
            return self.duracion or 'N/A'
        
        horas = self.duracion_segundos // 3600
        minutos = (self.duracion_segundos % 3600) // 60
        segundos = self.duracion_segundos % 60
        
        if horas > 0:
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        else:
            return f"{minutos:02d}:{segundos:02d}"
    
    @property
    def tiene_recursos(self):
        """Indica si la canción tiene enlaces o recursos"""
        return bool(self.link or self.link_partitura)
    
    @property
    def etiquetas_lista(self):
        """Devuelve las etiquetas como lista"""
        if not self.etiquetas:
            return []
        return [etiqueta.strip() for etiqueta in self.etiquetas.split(',') if etiqueta.strip()]
    
    @property
    def popularidad(self):
        """Calcula un índice de popularidad basado en veces tocada"""
        if self.veces_tocada == 0:
            return 'Nueva'
        elif self.veces_tocada <= 5:
            return 'Ocasional'
        elif self.veces_tocada <= 15:
            return 'Regular'
        else:
            return 'Popular'
    
    @property
    def dias_sin_tocar(self):
        """Calcula los días desde la última vez que se tocó"""
        if not self.ultima_vez_tocada:
            return None
        
        diferencia = timezone.now() - self.ultima_vez_tocada
        return diferencia.days
    
    def marcar_como_tocada(self):
        """Marca la canción como tocada, incrementando el contador"""
        self.veces_tocada += 1
        self.ultima_vez_tocada = timezone.now()
        self.save(update_fields=['veces_tocada', 'ultima_vez_tocada'])
    
    def agregar_etiqueta(self, nueva_etiqueta):
        """Agrega una nueva etiqueta si no existe"""
        etiquetas_actuales = self.etiquetas_lista
        if nueva_etiqueta not in etiquetas_actuales:
            etiquetas_actuales.append(nueva_etiqueta)
            self.etiquetas = ', '.join(etiquetas_actuales)
            self.save(update_fields=['etiquetas'])
    
    def quitar_etiqueta(self, etiqueta_a_quitar):
        """Quita una etiqueta específica"""
        etiquetas_actuales = self.etiquetas_lista
        if etiqueta_a_quitar in etiquetas_actuales:
            etiquetas_actuales.remove(etiqueta_a_quitar)
            self.etiquetas = ', '.join(etiquetas_actuales)
            self.save(update_fields=['etiquetas'])
    
    def marcar_favorita(self):
        """Marca la canción como favorita"""
        self.es_favorita = True
        self.save(update_fields=['es_favorita'])
    
    def quitar_favorita(self):
        """Quita la marca de favorita"""
        self.es_favorita = False
        self.save(update_fields=['es_favorita'])
