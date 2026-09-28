"""Modelos de organización y usuario."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Organizacion(models.Model):
    """La empresa dueña de los datos.

    Aunque de momento solo habrá una (la del tío), todo el modelo se
    filtra por organización desde el día uno. Cuando pasemos a SaaS,
    cada cliente será una organización más y no habrá que refactorizar.
    """

    nombre = models.CharField(max_length=200)
    nif = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"

    def __str__(self) -> str:
        return self.nombre


class UsuarioManager(BaseUserManager):
    """Gestor de usuarios que usa email como identificador."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superusuario debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superusuario debe tener is_superuser=True")
        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Usuario de la aplicación (login con email en lugar de username)."""

    ROL_ADMIN = "admin"
    ROL_ENCARGADO = "encargado"
    ROL_TRABAJADOR = "trabajador"
    ROLES = [
        (ROL_ADMIN, "Administrador"),
        (ROL_ENCARGADO, "Encargado"),
        (ROL_TRABAJADOR, "Trabajador"),
    ]

    username = None
    email = models.EmailField("email", unique=True)
    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE,
        related_name="usuarios",
        null=True,
        blank=True,
    )
    rol = models.CharField(max_length=20, choices=ROLES, default=ROL_ADMIN)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self) -> str:
        return self.email
