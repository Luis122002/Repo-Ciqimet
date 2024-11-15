from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta

# Modelo para almacenar los usuarios
class User(AbstractUser):
    class Role(models.TextChoices):
            SUPERVISOR = 'Supervisor', _('Supervisor')
            ADMINISTRADOR = 'Administrador', _('Administrador')
            QUIMICO = 'Quimico', _('Químico')
    
    class Turno(models.TextChoices):
        DIA = 'Dia', _('Dia')
        NOCHE = 'Noche', _('Noche')
            
    username = models.EmailField(_('Correo'), unique=True, null=False, blank=False)
    rut = models.CharField(max_length=200, unique=True, null=False, blank=False)
    token = models.CharField(max_length=200, null=True, blank=True)  # Único campo opcional
    rolname = models.CharField(max_length=200, choices=Role.choices)
    turno = models.CharField(max_length=200, choices=Turno.choices)
    date_joined = models.DateTimeField(_('Fecha de ingreso'), auto_now_add=True)
    
    def _str_(self):
        name = self.first_name + ' ' + self.last_name
        return name
    
# Modelo para almacenar los clientes y proyectos
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=False, blank=False)
    fecha_emision = models.DateField(null=False, blank=False)
    
    ### <
    def __str__(self):
        return self.nombre
    ### <

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    rut = models.CharField(max_length=100, null=False, blank=False)
    direccion = models.CharField(max_length=100, null=False, blank=False)
    telefono = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    
    def __str__(self):
        return self.nombre


# Modelos específicos para los diferentes tipos de análisis
class AnalisisCuTFeZn(models.Model):
    l_ppm_fe = models.FloatField(verbose_name="L. ppm Fe", null=False, blank=False)
    l_ppm_bk_fe = models.FloatField(verbose_name="L. ppm-BK Fe", null=False, blank=False)
    fe = models.FloatField(verbose_name="Fe (%)", null=False, blank=False)
    l_ppm_zn = models.FloatField(verbose_name="L. ppm Zn", null=False, blank=False)
    l_ppm_bk_zn = models.FloatField(verbose_name="L. ppm-BK Zn", null=False, blank=False)
    zn = models.FloatField(verbose_name="Zn (%)", null=False, blank=False)
    
    def __str__(self):
        return f"Análisis CuT-Fe-Zn"

class AnalisisCuS4FeS4MoS4(models.Model):
    control1_cut_cus = models.FloatField(verbose_name="Control1 CuT-CuS", null=False, blank=False)
    l_ppm_cus_fe = models.FloatField(verbose_name="L. ppm CusFe", null=False, blank=False)
    l_ppm_bk_fes4 = models.FloatField(verbose_name="L. ppm-BK FeS4", null=False, blank=False)
    fes4 = models.FloatField(verbose_name="FeS4 (%)", null=False, blank=False)
    control2_cut_fes4 = models.FloatField(verbose_name="Control2 CuT-FeS4", null=False, blank=False)
    
    def __str__(self):
        return f"Análisis CuS4-FeS4-MoS4"

class AnalisisMulti(models.Model):
    l_ppm_ag = models.FloatField(verbose_name="L. ppm Ag", null=False, blank=False)
    l_ppm_ag_bk = models.FloatField(verbose_name="L. ppm Ag-bk", null=False, blank=False)
    ag = models.FloatField(verbose_name="Ag (ppm)", null=False, blank=False)
    l_ppm_as = models.FloatField(verbose_name="L. ppm As", null=False, blank=False)
    l_ppm_as_bk = models.FloatField(verbose_name="L. ppm As-bk", null=False, blank=False)
    analisis_as = models.FloatField(verbose_name="As (%)", null=False, blank=False)
    l_ppm_mo = models.FloatField(verbose_name="L. ppm Mo", null=False, blank=False)
    l_ppm_mo_bk = models.FloatField(verbose_name="L. ppm Mo-bk", null=False, blank=False)
    mo = models.FloatField(verbose_name="Mo (%)", null=False, blank=False)
    l_ppm_pb = models.FloatField(verbose_name="L. ppm Pb", null=False, blank=False)
    l_ppm_pb_bk = models.FloatField(verbose_name="L. ppm Pb-Bk", null=False, blank=False)
    pb = models.FloatField(verbose_name="Pb (%)", null=False, blank=False)
    l_ppm_cu = models.FloatField(verbose_name="L. ppm Cu", null=False, blank=False)
    l_ppm_cu_bk = models.FloatField(verbose_name="L. ppm Cu-bk", null=False, blank=False)
    cu = models.FloatField(verbose_name="Cu (%)", null=False, blank=False)
    
    def __str__(self):
        return f"Análisis Multi"

class AnalisisCuS10FeS10MoS10(models.Model):
    control_cut_cus = models.FloatField(verbose_name="Control CuT-CuS", null=False, blank=False)
    cut = models.FloatField(verbose_name="CuT", null=False, blank=False)
    cus10 = models.FloatField(verbose_name="CuS10", null=False, blank=False)
    
    def __str__(self):
        return f"Análisis CuS10-FeS10-MoS10"

class AnalisisCuSCuSFe(models.Model):
    l_ppm_cus_fe = models.FloatField(verbose_name="L. ppm CuSFe", null=False, blank=False)
    l_ppm_bk_cus_fe = models.FloatField(verbose_name="L. ppm-Bk CuSFe", null=False, blank=False)
    cus_fe = models.FloatField(verbose_name="CuSFe (%)", null=False, blank=False)
    control2_cut_cus_fe = models.FloatField(verbose_name="Control2 CuT-CuSFe", null=False, blank=False)
    cut = models.FloatField(verbose_name="CuT", null=False, blank=False)
    cus_c = models.FloatField(verbose_name="CuSC", null=False, blank=False)
    cus_fe_2 = models.FloatField(verbose_name="CuSFe", null=False, blank=False)
    
    def __str__(self):
        return f"Análisis CuS3-CuSFe"

class AnalisisCuTestConsH(models.Model):
    control1_cut_cutest = models.FloatField(verbose_name="Control1 CuT-CuTest", null=False, blank=False)
    cut = models.FloatField(verbose_name="CuT", null=False, blank=False)
    cut_test = models.FloatField(verbose_name="CuTest", null=False, blank=False)
    gaston_ml = models.FloatField(verbose_name="Gaston mL", null=False, blank=False)
    gasto_bk_ml = models.FloatField(verbose_name="Gasto Bk mL", null=False, blank=False)
    n_naco3 = models.FloatField(verbose_name="N NaCO3", null=False, blank=False)
    alicuota = models.FloatField(verbose_name="Alicuota", null=False, blank=False)
    consumo_h = models.FloatField(verbose_name="Consumo H+", null=False, blank=False)
    
    def __str__(self):
        return f"Análisis CuTest-ConsH"



def validate_length(value):
    if len(str(value)) != 9:
        raise ValidationError('El número debe tener exactamente 9 dígitos.')


class ODT(models.Model):
    class T_MUESTRA(models.TextChoices):
        SONDAJE = 'Sondaje', _('Sondaje')
        SUBTERRANEA = 'Subterranea', _('Subterranea')
        TRONADURA = 'Tronadura', _('Tronadura')

    class PrioridadChoice(models.TextChoices):
        ALTA = 'Alta', _('Alta')
        MEDIA = 'Media', _('Media')
        BAJA = 'Baja', _('Baja')

    Fec_Recep = models.DateField()
    Fec_Finalizacion = models.DateField()
    id = models.CharField(_("Número de OT"), max_length=200, unique=True, primary_key=True)
    Prefijo = models.CharField("Muestra inicial", max_length=200, blank=True, null=True)
    Cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=False, blank=False)
    Proyecto = models.ForeignKey('Proyecto', on_delete=models.CASCADE, null=False, blank=False)
    Responsable = models.CharField(_("Responsable envío"), max_length=200, blank=True, null=True)
    Prioridad = models.CharField(_("Prioridad"), max_length=200, choices=PrioridadChoice.choices, blank=True)
    TipoMuestra = models.CharField(_("Tipo de Muestra"), max_length=200, choices=T_MUESTRA.choices, blank=True)
    Referencia = models.PositiveIntegerField(_("Batch"), blank=True, null=True)
    Comentarios = models.CharField(max_length=255, blank=True)
    Cant_Muestra = models.PositiveIntegerField(_("Cantidad de Muestras"), blank=True, null=True)

    def save(self, *args, **kwargs):
        if self._state.adding and not self.id:
            last_odt = ODT.objects.order_by('-id').first()
            if last_odt:
                try:
                    last_number = int(last_odt.id[3:])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            self.id = f'WSS{new_number:06d}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'WSS{ self.id}'
        
    
class MuestraMasificada(models.Model):
    odt = models.ForeignKey(ODT, on_delete=models.CASCADE, related_name='masificaciones')
    Prefijo = models.CharField(max_length=200,unique=True , primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipoMuestra = models.CharField(max_length=200 ,default='M')

    def __str__(self):
        return f'Muestra {self.Prefijo} para ODT {self.odt.id}'
    
    def clean(self):
    # Asegurarse de que Prefijo es una cadena
        if not isinstance(self.Prefijo, str):
            raise ValidationError("El campo Prefijo debe ser una cadena.")

class Elementos(models.Model):
    nombre = models.CharField(max_length=200 , unique=True)
    gramos = models.FloatField()
    miligramos = models.FloatField()

    def __str__(self):
        return f"{self.nombre} ({self.gramos}g / {self.miligramos}ml)"

class MetodoAnalisis(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name="cliente")
    nombre = models.CharField(max_length=200)
    metodologia = models.TextField()
    elementos = models.ManyToManyField(Elementos, related_name="elementos")
    
    def __str__(self):
        return f"Metodo {self.nombre}"
    

 ### >   
class CurvaturaElementos(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE) 
    elemento = models.ForeignKey(Elementos, on_delete=models.CASCADE, related_name="elemento")  
    curvatura = models.IntegerField(
        "Curvatura de análisis", 
        default=1, 
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cliente', 'elemento'], name='unique_cliente_elemento')
        ]

    def __str__(self):
        return f"{self.cliente.nombre} | {self.elemento.nombre} | Curvatura: {self.curvatura}"
### <

class Parametros(models.Model):
    Elementos = models.ManyToManyField(Elementos, related_name="Elementos")
    Unidad = models.CharField(max_length=200)
    VA = models.FloatField()
    DS = models.FloatField()
    Min = models.FloatField()
    Max = models.FloatField()

class Estandar(models.Model):
    Nombre = models.CharField(max_length=200, unique=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name="Clientes")
    parametros = models.ManyToManyField('Parametros', related_name="Parametro")

class HojaTrabajo(models.Model):
    odt = models.ForeignKey('ODT', on_delete=models.CASCADE, related_name='hojas_trabajo')
    Estandar = models.ManyToManyField('Estandar', related_name="Estandar")
    MetodoAnalisis = models.ForeignKey('MetodoAnalisis', on_delete=models.CASCADE, related_name="Metodo_de_Analisis")
    MuestraMasificada = models.ForeignKey('MuestraMasificada', on_delete=models.CASCADE, related_name="MuestraMasificada")
    Tipo = models.CharField(max_length=200, default='M')  # 'S' para estandar, 'D' para duplicado, 'B' para blanco
    Duplicado = models.CharField(max_length=200, blank=True, null=True)


class HojaTrabajoQuimico(models.Model):
    ### >
    ID_HDT = models.CharField(_("Nro Hoja de trabajo"), max_length=200, blank=False, null=False)
    confirmar_balanza = models.BooleanField(default=False, verbose_name="Confirmar_Balanza")
    confirmar_Absorcion = models.BooleanField(default=False, verbose_name="Confirmar_Absorción")
    ### <
    HojaTrabajo=models.ForeignKey(HojaTrabajo, on_delete=models.CASCADE, related_name='hojas_trabajo_target')


# Modelo general para almacenar asociadas a una muestra de análisis
class Muestra(models.Model):
    nombre = models.CharField(max_length=100, null=False, blank=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=False, blank=False)
    fecha_emision = models.DateField(null=False, blank=False)
    elemento = models.CharField(max_length=100, null=False, blank=False)
    nbo = models.CharField(max_length=100, null=False, blank=False)
    ident = models.CharField(max_length=100, null=False, blank=False)
    
    ### >
    indexCurv = models.IntegerField("posisión de curvatura",default=1, validators=[MinValueValidator(1)] )
    hoja_trabajo = models.ForeignKey(HojaTrabajo, on_delete=models.CASCADE, related_name="hoja_de_trabajo")
    muestraMasificada = models.ForeignKey(MuestraMasificada, on_delete=models.CASCADE, related_name="muestra_masificada", default=None, null=False, blank=True)
    ### <
    t = models.CharField(max_length=100, null=False, blank=False)
    peso_m = models.FloatField(verbose_name="PesoM. (g)", null=False, blank=False)
    v_ml = models.FloatField(verbose_name="V. mL", null=False, blank=False)
    l_ppm = models.FloatField(verbose_name="L. ppm", null=False, blank=False)
    l_ppm_bk = models.FloatField(verbose_name="L. ppm-BK", null=False, blank=False)
    porcentaje = models.FloatField(verbose_name="Porcentaje (%)", null=False, blank=False)
    
    def __str__(self):
        return f"Muestra {self.nombre} de {self.elemento}"
    

class LotesAbsorción(models.Model):
    ID_HDT = models.CharField(_("Nro de Lote"), max_length=200, blank=False, null=False)
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name="muestra_de_analisis")


# Modelo para almacenar los resultados
### >
class Resultado(models.Model):
    elemento = models.ForeignKey(Elementos, on_delete=models.CASCADE, related_name="resultados")
    muestra = models.ForeignKey(MuestraMasificada, on_delete=models.CASCADE, related_name="resultados")
    hoja_trabajo = models.ForeignKey(HojaTrabajo, on_delete=models.CASCADE, related_name="resultados")
    resultadoAnalisis = models.FloatField(verbose_name="Resultado de Análisis", null=False, blank=False)
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión", null=False, blank=False)
### <

class Novedades(models.Model):
    class Tipo(models.TextChoices):
        ORDEN_DE_TRABAJO = 'Orden_de_trabajo', _('Orden de trabajo')
        HOJA_DE_TRABAJO = 'Hoja_de_trabajo', _('Hoja de trabajo')

    class Accion(models.TextChoices):
        CREAR = 'Crear', _('Crear')
        MODIFICAR = 'Modificar', _('Modificar')
        ELIMINAR = 'Eliminar', _('Eliminar')
        BALANZA = 'Balanza', _('Balanza')
        ABSORCION = 'Absorcion', _('Absorción')

    tipo_model = models.CharField(max_length=200, choices=Tipo.choices)
    accion = models.CharField(max_length=200, choices=Accion.choices)
    modelt_id = models.CharField(max_length=200, verbose_name="ID registro") 
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=200)  

    def __str__(self):
        return f"{self.tipo_model} - {self.accion} - {self.modelt_id} - {self.fecha}"

    class Meta:
        verbose_name_plural = "Novedades"

    @classmethod
    def eliminar_antiguos(cls):
        limite = timezone.now() - timedelta(days=30)
        cls.objects.filter(fecha__lt=limite).delete()
