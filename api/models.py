from django.contrib.auth.models import AbstractUser 
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENTE = 'Cliente', _('Cliente')
        SUPERVISOR = 'Supervisor', _('Supervisor')
        ADMINISTRADOR = 'Administrador', _('Administrador')
        QUIMICO_A = 'QuimicoA', _('Químico A')
        QUIMICO_B = 'QuimicoB', _('Químico B')
        QUIMICO_C = 'QuimicoC', _('Químico C')

    rut = models.CharField(max_length=200, null=True, blank=True)
    rolname = models.CharField(max_length=200, choices=Role.choices, default=Role.CLIENTE)
    is_superuser = models.BooleanField(default=False)
    credential = models.CharField(_("Credential"), max_length=50, blank=True)

    def __str__(self):
        return self.username  # Cambié esto a `username` para representar al usuario de manera más estándar.

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'rolname': User.Role.CLIENTE})
    nombre_cliente = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación

    def __str__(self):
        return self.nombre_cliente

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.CASCADE, related_name='proyectos')
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación
    volVal = models.FloatField(_("uso de volumen"), default=0.0, blank=True, null=True)

    def __str__(self):
        return self.nombre

class ODT(models.Model):
    id = models.AutoField(primary_key=True)
    Nro_OT = models.CharField(_("Código de ODT"), max_length=200, unique=True)
    Fec_Recep = models.DateField()
    Cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.CASCADE)
    Proyecto = models.ForeignKey(Proyecto, null=True, blank=True, on_delete=models.CASCADE)
    Despacho = models.CharField(_("Despacho"),max_length=200, blank=True, null=True)
    Envio = models.ForeignKey(User, limit_choices_to={'rolname__in': [User.Role.QUIMICO_A, User.Role.QUIMICO_B, User.Role.QUIMICO_C]}, on_delete=models.CASCADE, related_name='envios', verbose_name=_("Responsable de envío"))
    Muestra = models.CharField(_("Código de muestras"), max_length=200)
    Comentarios = models.CharField(max_length=255, blank=True)
    Turno = models.CharField(
        _("Turno"),
        max_length=10,
        choices=[('DIA', _('Día')), ('NOCHE', _('Noche'))],
        default='DIA'
    )
    InicioCodigo = models.PositiveIntegerField(_("Inicio Código"), blank=True, null=True)
    FinCodigo = models.PositiveIntegerField(_("Fin Código"), blank=True, null=True)
    Cant_Muestra = models.PositiveIntegerField(_("Cantidad de Muestras"), blank=True, null=True)
    
    Analisis = models.ForeignKey('Analisis', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Análisis"))
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación

    def __str__(self):
        return self.Nro_OT

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.InicioCodigo is not None and self.FinCodigo is not None:
                self.Cant_Muestra = self.FinCodigo - self.InicioCodigo + 1
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.InicioCodigo is not None and self.FinCodigo is not None:
            if self.FinCodigo < self.InicioCodigo:
                raise ValidationError('El número final del código debe ser mayor o igual al número inicial.')
        if self.Muestra and self.InicioCodigo is not None and self.FinCodigo is not None:
            overlapping_records = ODT.objects.exclude(id=self.id).filter(
                Muestra=self.Muestra,
                InicioCodigo__lte=self.FinCodigo,
                FinCodigo__gte=self.InicioCodigo
            )
            if overlapping_records.exists():
                raise ValidationError(
                    'El rango de códigos de muestra ({0}-{1}) se solapa con un rango existente para el código de muestra {2}.'.format(
                        self.InicioCodigo, self.FinCodigo, self.Muestra
                    )
                )
        if self.Muestra and self.InicioCodigo is not None and self.FinCodigo is not None:
            for codigo in range(self.InicioCodigo, self.FinCodigo + 1):
                expected_id_muestra = f"{self.Muestra}-{codigo:03d}"
                if OT.objects.filter(id_muestra=expected_id_muestra).exists():
                    raise ValidationError(
                        f'El código de muestra {expected_id_muestra} ya existe en OT.'
                    )

class Analisis(models.Model):
    id = models.AutoField(primary_key=True)
    Analisis_metodo = models.CharField(_("Método de análisis"), max_length=200)
    Nro_Analisis = models.CharField(_("Código de análisis"), max_length=200, unique=True, null=True)
    descripcion = models.CharField(max_length=255)
    Formula = models.CharField(max_length=255)
    Elementos = models.ManyToManyField('Elementos', verbose_name=_("Elementos"), blank=True)  # Relación con Elementos
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación

    def __str__(self):
        return self.Analisis_metodo
    

class Elementos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(max_length=255, blank=True)
    tipo = models.CharField(max_length=200)
    enabled = models.BooleanField(_("Activo"), default=True)
    simbolo = models.CharField(max_length=5, blank=True, null=True)
    numero_atomico = models.IntegerField(blank=True, null=True) 
    masa_atomica = models.FloatField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación

    def __str__(self):
        return self.nombre

class OT(models.Model):
    id = models.AutoField(primary_key=True)
    id_muestra = models.CharField(_("ID Muestra"), max_length=50, unique=True)
    peso_muestra = models.FloatField(_("Peso Muestra"))
    volumen = models.FloatField(_("Volumen"))
    dilucion = models.FloatField(_("Dilución"))
    odt = models.ForeignKey(ODT, on_delete=models.CASCADE, related_name="ots")
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación

    def __str__(self):
        return self.id_muestra

