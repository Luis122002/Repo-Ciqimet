from django.contrib.auth.models import AbstractUser 
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
    Nro_OT = models.CharField(max_length=200)
    Fec_Recep = models.DateField()
    Cant_Muestra = models.IntegerField(_("Cantidad Muestra"))
    Cliente = models.CharField(max_length=200)
    Proyecto = models.CharField(max_length=200)
    Despacho = models.CharField(max_length=200)
    Envio = models.CharField(max_length=200)
    Muestra = models.CharField(_("Codigo de muestras"),max_length=200)
    Referencia = models.CharField(max_length=200)
    Comentarios = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.Nro_OT


class Analisis(models.Model):
    id = models.AutoField(primary_key=True)
    Analisis_metodo = models.CharField(_("Método de Análisis"), max_length=200)
    descripcion = models.CharField(max_length=255)
    Formula = models.CharField(max_length=255)

    def __str__(self):
        return self.Analisis_metodo


class OT(models.Model):
    id = models.AutoField(primary_key=True)
    id_muestra = models.CharField(_("ID Muestra"), max_length=50)
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