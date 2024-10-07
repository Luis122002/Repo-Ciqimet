import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
import datetime
from django.db import models
from django.utils.translation import gettext as _


def validate_length(value):
    if len(str(value)) != 8:  # Aquí defines la lógica de validación
        raise ValidationError(f'El número {value} debe tener exactamente 8 dígitos.')



# Modelo para almacenar los usuarios
class User(AbstractUser):
    class Role(models.TextChoices):
            CLIENTE = 'Cliente', _('Cliente')
            SUPERVISOR = 'Supervisor', _('Supervisor')
            ADMINISTRADOR = 'Administrador', _('Administrador')
            QUIMICO_A = 'QuimicoA', _('Químico A')
            QUIMICO_B = 'QuimicoB', _('Químico B')
            QUIMICO_C = 'QuimicoC', _('Químico C')
    username = models.EmailField(_('Correo'), unique=True, null=False, blank=False)
    rut = models.CharField(max_length=200, unique=True, null=False, blank=False, default="00000000-0")
    token = models.CharField(max_length=200, null=True, blank=True)  # Único campo opcional
    is_administrador = models.BooleanField('Administrador', default=False)
    is_supervisor = models.BooleanField('Supervisor', default=False)
    is_quimico = models.BooleanField('Químico', default=False)
    is_new_user = models.CharField(max_length=200, null=True, blank=True)
    date_joined = models.DateTimeField(_('Fecha de ingreso'), auto_now_add=True)
    rolname = models.CharField(max_length=200, choices=Role.choices)


    def __str__(self):
        name = self.first_name + ' ' + self.last_name
        return name


# Modelo para almacenar los clientes y proyectos
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, blank=False)
    fecha_emision = models.DateField(null=False, blank=False, default=datetime.date.today)
    volVal = models.FloatField(blank=True, null=True)
    def __str__(self):
        return self.cliente.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False, default="Desconocido")
    rut = models.CharField(max_length=100, null=False, blank=False, default="Desconocido")
    direccion = models.CharField(max_length=100, null=False, blank=False, default="Desconocido")
    telefono = models.CharField(max_length=100, null=False, blank=False, default="Desconocido")
    email = models.EmailField(null=False, blank=False, default="Desconocido")
    
    def __str__(self):
        return self.nombre


class ODT(models.Model):
    class T_MUESTRA(models.TextChoices):
        SONDAJE = 'Sondaje', _('Sondaje')
        SUBTERRANEA = 'Subterranea', _('Subterranea')
        TRONADURA = 'Tronadura', _('Tronadura')

    class PrioridadChoice(models.TextChoices):
        ALTA = 'Alta', _('Alta')
        MEDIA = 'Media', _('Media')
        BAJA = 'Baja', _('Baja')

    id = models.AutoField(primary_key=True)
    Nro_OT = models.CharField(_("Código de ODT"), max_length=200, unique=True)
    Fec_Recep = models.DateField()
    Cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.CASCADE)
    Proyecto = models.ForeignKey(Proyecto, null=True, blank=True, on_delete=models.CASCADE)
    Despacho = models.CharField(_("Despacho"), max_length=200, blank=True, null=True)
    Envio = models.ForeignKey(User, limit_choices_to={'rolname__in': [User.Role.QUIMICO_A, User.Role.QUIMICO_B, User.Role.QUIMICO_C]}, on_delete=models.CASCADE, related_name='envios', verbose_name=_("Responsable de envío"))
    Prefijo = models.PositiveIntegerField(_("Codigo de muestras"),validators=[validate_length], unique=True, blank=True, null=True)
    Comentarios = models.CharField(max_length=255, blank=True)
    Turno = models.CharField(_("Turno"), max_length=10, choices=[('DIA', _('Día')), ('NOCHE', _('Noche'))], default='DIA')
    InicioCodigo = models.PositiveIntegerField(_("Inicio Código"), blank=True, null=True)
    FinCodigo = models.PositiveIntegerField(_("Fin Código"), blank=True, null=True)
    Cant_Muestra = models.PositiveIntegerField(_("Cantidad de Muestras"), blank=True, null=True)
    Prioridad = models.CharField(_("Prioridad"), max_length=200, choices=PrioridadChoice.choices, blank=True)
    TipoMuestra = models.CharField(_("Tipo de Muestra"), max_length=200, choices=T_MUESTRA.choices, blank=True)
    Referencia = models.PositiveIntegerField(_("Batch"), blank=True, null=True)

    Analisis = models.ForeignKey('Analisis', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Análisis"))
    updated_at = models.DateTimeField(auto_now=True)  
    def save(self, *args, **kwargs):
        if not self.Nro_OT:
            last_odt = ODT.objects.order_by('id').last()
            if last_odt:
                last_ot_number = int(last_odt.Nro_OT.split('OT')[-1]) 
                self.Nro_OT = f"OT{last_ot_number + 1:06d}"
            else:
                self.Nro_OT = "OT000001"

        if not self.Prefijo and self.InicioCodigo and self.FinCodigo:
            self.Prefijo = f"M-{self.InicioCodigo}-{self.FinCodigo}"

        if self.Proyecto and self.Proyecto.cliente:
            self.Cliente = self.Proyecto.cliente

        super().save(*args, **kwargs)

    def __str__(self):
        return self.Nro_OT

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
        if self.Prefijo and self.InicioCodigo is not None and self.FinCodigo is not None:
            overlapping_records = ODT.objects.exclude(id=self.id).filter(
                Prefijo=self.Prefijo,
                InicioCodigo__lte=self.FinCodigo,
                FinCodigo__gte=self.InicioCodigo
            )
            if overlapping_records.exists():
                raise ValidationError(
                    'El rango de códigos de muestra ({0}-{1}) se solapa con un rango existente para el código de muestra {2}.'.format(
                        self.InicioCodigo, self.FinCodigo, self.Prefijo
                    )
                )
        if self.Prefijo and self.InicioCodigo is not None and self.FinCodigo is not None:
            for codigo in range(self.InicioCodigo, self.FinCodigo + 1):
                expected_id_muestra = f"{self.Prefijo}-{codigo:03d}"
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
    enabled = models.BooleanField(_("Activo"), default=True)

    def __str__(self):
        return self.Analisis_metodo

class Elementos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(_("Nombre"), max_length=200)
    tipo = models.CharField(max_length=200)
    simbolo = models.CharField(max_length=5, blank=True, null=True)
    numero_atomico = models.IntegerField(blank=True, null=True) 
    masa_atomica = models.FloatField(blank=True, null=True)
    enabled = models.BooleanField(_("Activo"), default=True)
    descripcion = models.TextField(max_length=255, blank=True)
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




class HojaTrabajo(models.Model):
    id_ht = models.AutoField(primary_key=True)
    nro_ht = models.CharField(max_length=100)
    fec_ht = models.DateField(auto_now=True)
    analisis = models.TextField()
    cant_muestras = models.ForeignKey(ODT, on_delete=models.CASCADE, related_name="hojas_trabajo")  # Cambiado el related_name
    ot_cliente = models.CharField(max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="hojas_trabajo_cliente")  # Cambiado el related_name
    odt = models.ForeignKey(ODT, on_delete=models.CASCADE, related_name="hojas_odt")  # Cambiado el related_name
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="hojas_proyecto")  # Cambiado el related_name
    envio = models.BooleanField(default=False)
    en_uso_por = models.CharField(max_length=255, null=True, blank=True)

    def str(self):
        return self.nro_ht