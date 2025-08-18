# AUTH/models.py
from django.contrib.auth.models import AbstractUser, UserManager
from core.models import BaseModel, BaseModelManager
from django.db import models


class UserCustomManager(BaseModelManager, UserManager):
    def get_queryset(self):
        return super(UserManager, self).get_queryset().filter(deleted_at__isnull=True)
    
    def _create_user(self, username, email, password, **extra_fields):
        return super(BaseModelManager, self)._create_user(username, email, password, **extra_fields)


class UserCustom(AbstractUser, BaseModel):
    objects = UserCustomManager()
    
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre de usuario",
        help_text="Nombre de usuario",
        null=False
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Nombres",
        help_text="Nombres",
        null = False
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name="Apellidos",
        help_text="Apellidos",
        null = False
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Email",
        help_text="Email",
        null=False
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Password",
        help_text="Password",
        null=False
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Teléfono",
        null = False,
        unique=True
    )
    image_profile = models.ImageField(
        upload_to='profile_pictures/',
        verbose_name="Imagen de perfil",
        help_text="Imagen de perfil",
        null=True,
        blank=True
    )
    birthday = models.DateField(
        verbose_name="Fecha de nacimiento",
        help_text="Fecha de nacimiento",
        null=True,
        blank=True,
    )
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name="Genero",
        help_text="Genero",
        null=True,
        blank=True,
    )
    
    ROLE_CHOICES = [
        ('root', 'Root'),
        ('admin', 'Administrador'),
        ('client', 'Cliente'),
    ]
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Rol",
        db_index=True,
        help_text="Rol del usuario"
    )
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-created_at']