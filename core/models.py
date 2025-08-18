from django.db import models

"""  B A S E   M O D E L   """
class BaseModel(models.Model):
    is_active = models.BooleanField(
        default=True,
        verbose_name="Estado",
        db_index=True,
        help_text="Indica si el registro se encuentra activo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
        db_index=True,
        help_text="Fecha y hora de creación del registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
        db_index=True,
        help_text="Fecha y hora de la ultima actualización del registro"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de borrado",
        db_index=True,
        help_text="Fecha y hora de borrado del registro"
    )
    
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

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
    
    