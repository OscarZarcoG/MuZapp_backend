from django.db import models


class Pais(models.Model):
    """Modelo para países"""
    nombre = models.CharField(max_length=50, blank=False, default='')
    
    class Meta:
        db_table = 'paises'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
    
    def __str__(self):
        return self.nombre


class Estado(models.Model):
    """Modelo para estados/provincias"""
    nombre = models.CharField(max_length=50, blank=False, default='')
    pais = models.ForeignKey(
        Pais, 
        on_delete=models.CASCADE,
        db_index=True,
        related_name='estados'
    )
    
    class Meta:
        db_table = 'estados'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        indexes = [
            models.Index(fields=['pais'], name='index_pais'),
        ]
    
    def __str__(self):
        return f"{self.nombre}, {self.pais.nombre}"


class Municipio(models.Model):
    """Modelo para municipios"""
    nombre = models.CharField(max_length=50, blank=False, default='')
    estado = models.ForeignKey(
        Estado,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='municipios'
    )
    
    class Meta:
        db_table = 'municipios'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        indexes = [
            models.Index(fields=['estado'], name='index_estado'),
        ]
    
    def __str__(self):
        return f"{self.nombre}, {self.estado.nombre}"


class Colonia(models.Model):
    """Modelo para colonias/asentamientos"""
    nombre = models.CharField(max_length=100, blank=False, default='')
    ciudad = models.CharField(max_length=50, blank=True, null=True)
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True,
        related_name='colonias'
    )
    asentamiento = models.CharField(max_length=25, blank=True, null=True)
    codigo_postal = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'colonias'
        verbose_name = 'Colonia'
        verbose_name_plural = 'Colonias'
        indexes = [
            models.Index(fields=['municipio'], name='index_municipio'),
            models.Index(fields=['nombre'], name='index_nombre'),
            models.Index(fields=['asentamiento'], name='index_asentamiento'),
            models.Index(fields=['codigo_postal'], name='index_codigo_postal'),
            models.Index(fields=['ciudad'], name='index_ciudad'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo_postal})"
