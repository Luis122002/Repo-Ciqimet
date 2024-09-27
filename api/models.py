import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


# Modelo para almacenar los usuarios
class User(AbstractUser):
    class Role(models.TextChoices):
            CLIENTE = 'Cliente', _('Cliente')
            SUPERVISOR = 'Supervisor', _('Supervisor')
            ADMINISTRADOR = 'Administrador', _('Administrador')
            QUIMICO_A = 'QuimicoA', _('Químico A')
            QUIMICO_B = 'QuimicoB', _('Químico B')
            QUIMICO_C = 'QuimicoC', _('Químico C')
            
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rut = models.CharField(max_length=200, null=True, blank=True)
    rolname = models.CharField(max_length=200, choices=Role.choices, default=Role.CLIENTE)
    is_superuser = models.BooleanField(default=False)
    credential = models.CharField(_("Credential"), max_length=50, blank=True)

    def __str__(self):
        return self.username  

# Modelo para almacenar los clientes y proyectos
class Proyecto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=False, blank=False)
    fecha_emision = models.DateField(null=False, blank=False)
    
    def __str__(self):
        return self.cliente.nombre

class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    rut = models.CharField(max_length=100, null=False, blank=False)
    direccion = models.CharField(max_length=100, null=False, blank=False)
    telefono = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    
    def __str__(self):
        return self.nombre


class ODT(models.Model):
    id = models.AutoField(primary_key=True)
    Nro_OT = models.CharField(_("Código de ODT"), max_length=200, unique=True)
    Fec_Recep = models.DateField()
    Cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.CASCADE)
    Proyecto = models.ForeignKey(Proyecto, null=True, blank=True, on_delete=models.CASCADE)
    Despacho = models.CharField(_("Despacho"), max_length=200, blank=True, null=True)
    Envio = models.ForeignKey(User, limit_choices_to={'rolname__in': [User.Role.QUIMICO_A, User.Role.QUIMICO_B, User.Role.QUIMICO_C]}, on_delete=models.CASCADE, related_name='envios', verbose_name=_("Responsable de envío"))
    Muestra = models.CharField(_("Código de muestras"), max_length=200)
    Comentarios = models.CharField(max_length=255, blank=True)
    Turno = models.CharField(_("Turno"), max_length=10, choices=[('DIA', _('Día')), ('NOCHE', _('Noche'))], default='DIA')
    InicioCodigo = models.PositiveIntegerField(_("Inicio Código"), blank=True, null=True)
    FinCodigo = models.PositiveIntegerField(_("Fin Código"), blank=True, null=True)
    Cant_Muestra = models.PositiveIntegerField(_("Cantidad de Muestras"), blank=True, null=True)
    Analisis = models.ForeignKey('Analisis', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Análisis"))
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última modificación

    def save(self, *args, **kwargs):
        # Asignar automáticamente el Cliente del Proyecto al guardar ODT
        if self.Proyecto and self.Proyecto.cliente:
            self.Cliente = self.Proyecto.cliente

        # Automatizar Nro_OT si no existe
        if not self.Nro_OT:
            last_odt = ODT.objects.order_by('id').last()
            if last_odt:
                last_ot_number = int(last_odt.Nro_OT.split('OT')[-1])  # Suponiendo que el formato es 'OT123456'
                self.Nro_OT = f"OT{last_ot_number + 1:06d}"
            else:
                self.Nro_OT = "OT000001"

        # Automatizar el campo de muestra si no está definido
        if not self.Muestra and self.InicioCodigo and self.FinCodigo:
            self.Muestra = f"M-{self.InicioCodigo}-{self.FinCodigo}"

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

