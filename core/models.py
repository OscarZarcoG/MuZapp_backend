from django.db import models

"""  B A S E   M O D E L   """
class BaseModelManager(models.Manager):    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def all_with_deleted(self):
        return super().get_queryset()
    
    def deleted_only(self):
        return super().get_queryset().filter(deleted_at__isnull=False)
    
    def active_only(self):
        return self.get_queryset().filter(is_active=True)
    
class BaseModel(models.Model):
    objects = BaseModelManager()
    
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

    def delete(self, using=None, keep_parents=False, user=None, force_hard_delete=False):
        from django.utils import timezone
        
        if force_hard_delete and user and hasattr(user, 'role') and user.role == 'root':
            return super().delete(using=using, keep_parents=keep_parents)
        
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
        
    def hard_delete(self, using=None, keep_parents=False, user=None):
        if not user or not hasattr(user, 'role') or user.role != 'root':
            raise PermissionError("Solo el usuario root puede realizar borrado completo")
        
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()

    def is_deleted(self):
        return self.deleted_at is not None

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"