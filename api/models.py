from django.contrib.auth.models import AbstractUser 
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.
# Modelo para almacenar los usuarios
class User(AbstractUser):
    rut = models.CharField(max_length=200, null=True, blank=True)
    rolname = models.CharField(max_length=200, null=False, blank=True)
    is_superuser = models.BooleanField(default=False)
    credential = models.CharField(_("Credential"), max_length=50, blank=True)

    def __str__(self):
        return self.rolname

class ODT(models.Model):
    id = models.AutoField(primary_key=True)
    Nro_OT = models.CharField(max_length=200, unique=True)
    Fec_Recep = models.DateField()
    Cliente = models.CharField(max_length=200)
    Proyecto = models.CharField(max_length=200)
    Despacho = models.CharField(max_length=200)
    Envio = models.CharField(max_length=200)
    Muestra = models.CharField(_("Código de muestras"), max_length=200)
    Referencia = models.CharField(max_length=200)
    Comentarios = models.CharField(max_length=255, blank=True)
    InicioCodigo = models.PositiveIntegerField(_("Inicio Código"), blank=True, null=True)
    FinCodigo = models.PositiveIntegerField(_("Fin Código"), blank=True, null=True)
    Cant_Muestra = models.PositiveIntegerField(_("Cantidad de Muestras"), blank=True, null=True)  # Campo para almacenar Cant_Muestra
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de actualización automática

    def __str__(self):
        return self.Nro_OT

    def save(self, *args, **kwargs):
        # Solo actualizar Cant_Muestra si es una nueva instancia
        if self.pk is None:  # La instancia es nueva
            if self.InicioCodigo is not None and self.FinCodigo is not None:
                self.Cant_Muestra = self.FinCodigo - self.InicioCodigo + 1
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Verificar que FinCodigo sea mayor o igual a InicioCodigo
        if self.InicioCodigo is not None and self.FinCodigo is not None:
            if self.FinCodigo < self.InicioCodigo:
                raise ValidationError('El número final del código debe ser mayor o igual al número inicial.')

        # Verificar la unicidad del código dentro del rango en ODT
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

        # Verificar la existencia del id_muestra en OT
        if self.Muestra and self.InicioCodigo is not None and self.FinCodigo is not None:
            for codigo in range(self.InicioCodigo, self.FinCodigo + 1):
                expected_id_muestra = f"{self.Muestra}-{codigo:03d}"
                if OT.objects.filter(id_muestra=expected_id_muestra).exists():
                    raise ValidationError(
                        f'El código de muestra {expected_id_muestra} ya existe en OT.'
                    )

class Analisis(models.Model):
    id = models.AutoField(primary_key=True)
    Analisis_metodo = models.CharField(_("Método de Análisis"), max_length=200)
    descripcion = models.CharField(max_length=255)
    Formula = models.CharField(max_length=255)

    def __str__(self):
        return self.Analisis_metodo


class OT(models.Model):
    id = models.AutoField(primary_key=True)
    id_muestra = models.CharField(_("ID Muestra"), max_length=50, unique=True)
    peso_muestra = models.FloatField(_("Peso Muestra"))
    volumen = models.FloatField(_("Volumen"))
    dilucion = models.FloatField(_("Dilución"))
    odt = models.ForeignKey(ODT, on_delete=models.CASCADE, related_name="ots")
    analisis = models.ForeignKey(Analisis, on_delete=models.CASCADE, related_name="ots",null=True)

    def __str__(self):
        return self.id_muestra


class Elementos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(max_length=255, blank=True)
    tipo = models.CharField(max_length=200)
    enabled = models.BooleanField(_("Activo"),default=True)
    simbolo = models.CharField(max_length=5, blank=True, null=True)
    numero_atomico = models.IntegerField(blank=True, null=True) 
    masa_atomica = models.FloatField(blank=True, null=True)
 
    def __str__(self):
        return self.nombre

class LecturasElementos(models.Model):
    id = models.AutoField(primary_key=True)
    lectura = models.IntegerField(_("Lectura"))
    analisis = models.ForeignKey(Analisis, on_delete=models.CASCADE, related_name="lecturas_elementos")
    ot = models.ForeignKey(OT, on_delete=models.CASCADE, related_name="lecturas_elementos")
    elementos = models.ForeignKey(Elementos, on_delete=models.CASCADE, related_name="lecturas_elementos")

    def __str__(self):
        return f"{self.lectura} - {self.analisis} - {self.ot} - {self.elementos}"