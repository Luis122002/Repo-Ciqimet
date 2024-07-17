from django.contrib.auth.models import AbstractUser 
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.
# Modelo para almacenar los usuarios
class User(AbstractUser):
    username = models.EmailField(_('Correo'), unique=True)
    rut = models.CharField(max_length=200 , null=True,blank=True)
    token= models.CharField(max_length=200 , null=True,blank=True)
    is_administrador = models.BooleanField('Administrador', default=False)
    is_supervisor = models.BooleanField('is_supervisor', default=False)
    is_quimico = models.BooleanField('is_quimico', default=False)
    is_cliente = models.BooleanField('is_cliente', default=False)
    is_new_user= models.CharField(max_length=200 , null=True,blank=True)
    date_joined = models.DateTimeField(_('Fecha de ingreso'), auto_now_add=True)
    
    def __str__(self):
        name = self.first_name + ' ' + self.last_name
        return name


# Modelo para almacenar los elementos
class Elemento(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

# Modelo general para almacenar la información básica de una muestra
class Muestra(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_emision = models.DateField()
    
    def __str__(self):
        return self.nombre

# Modelo general para almacenar las submuestras asociadas a una muestra
class Submuestra(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='submuestras')
    elemento = models.ForeignKey(Elemento, on_delete=models.CASCADE)
    nbo = models.CharField(max_length=100, blank=True, null=True)
    ident = models.CharField(max_length=100, blank=True, null=True)
    t = models.CharField(max_length=100, blank=True, null=True)
    peso_m = models.FloatField(verbose_name="PesoM. (g)", blank=True, null=True)
    v_ml = models.FloatField(verbose_name="V. mL", blank=True, null=True)
    l_ppm = models.FloatField(verbose_name="L. ppm", blank=True, null=True)
    l_ppm_bk = models.FloatField(verbose_name="L. ppm-BK", blank=True, null=True)
    porcentaje = models.FloatField(verbose_name="Porcentaje (%)", blank=True, null=True)
    
    class Meta:
        abstract = True

# Modelos específicos para los diferentes tipos de análisis

class AnalisisCuTFeZn(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis_cutfezn')
    l_ppm_fe = models.FloatField(verbose_name="L. ppm Fe", blank=True, null=True)
    l_ppm_bk_fe = models.FloatField(verbose_name="L. ppm-BK Fe", blank=True, null=True)
    fe = models.FloatField(verbose_name="Fe (%)", blank=True, null=True)
    l_ppm_zn = models.FloatField(verbose_name="L. ppm Zn", blank=True, null=True)
    l_ppm_bk_zn = models.FloatField(verbose_name="L. ppm-Bk Zn", blank=True, null=True)
    zn = models.FloatField(verbose_name="Zn (%)", blank=True, null=True)
    
    def __str__(self):
        return f"Análisis CuT-Fe-Zn: {self.elemento}"

class AnalisisCuS4FeS4MoS4(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis_cus4fes4mos4')
    control1_cut_cus = models.FloatField(verbose_name="Control1 CuT-CuS", blank=True, null=True)
    l_ppm_cus_fe = models.FloatField(verbose_name="L. ppm CusFe", blank=True, null=True)
    l_ppm_bk_fes4 = models.FloatField(verbose_name="L. ppm-BK FeS4", blank=True, null=True)
    fes4 = models.FloatField(verbose_name="FeS4 (%)", blank=True, null=True)
    control2_cut_fes4 = models.FloatField(verbose_name="Control2 CuT-FeS4", blank=True, null=True)
    
    def __str__(self):
        return f"Análisis CuS4-FeS4-MoS4: {self.elemento}"

class AnalisisMulti(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis_multi')
    l_ppm_ag = models.FloatField(verbose_name="L. ppm Ag", blank=True, null=True)
    l_ppm_ag_bk = models.FloatField(verbose_name="L. ppm Ag-bk", blank=True, null=True)
    ag = models.FloatField(verbose_name="Ag (ppm)", blank=True, null=True)
    l_ppm_as = models.FloatField(verbose_name="L. ppm As", blank=True, null=True)
    l_ppm_as_bk = models.FloatField(verbose_name="L. ppm As-bk", blank=True, null=True)
    analisis_as = models.FloatField(verbose_name="As (%)", blank=True, null=True)
    l_ppm_mo = models.FloatField(verbose_name="L. ppm Mo", blank=True, null=True)
    l_ppm_mo_bk = models.FloatField(verbose_name="L. ppm Mo-bk", blank=True, null=True)
    mo = models.FloatField(verbose_name="Mo (%)", blank=True, null=True)
    l_ppm_pb = models.FloatField(verbose_name="L. ppm Pb", blank=True, null=True)
    l_ppm_pb_bk = models.FloatField(verbose_name="L. ppm Pb-Bk", blank=True, null=True)
    pb = models.FloatField(verbose_name="Pb (%)", blank=True, null=True)
    l_ppm_cu = models.FloatField(verbose_name="L. ppm Cu", blank=True, null=True)
    l_ppm_cu_bk = models.FloatField(verbose_name="L. ppm Cu-bk", blank=True, null=True)
    cu = models.FloatField(verbose_name="Cu (%)", blank=True, null=True)
    
    def __str__(self):
        return f"Análisis Multi: {self.elemento}"

class AnalisisCuS10FeS10MoS10(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis_cus10fes10mos10')
    control_cut_cus = models.FloatField(verbose_name="Control CuT-CuS", blank=True, null=True)
    cut = models.FloatField(verbose_name="CuT", blank=True, null=True)
    cus10 = models.FloatField(verbose_name="CuS10", blank=True, null=True)
    
    def __str__(self):
        return f"Análisis CuS10-FeS10-MoS10: {self.elemento}"

class AnalisisCuSCuSFe(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis_cuscusfe')
    l_ppm_cus_fe = models.FloatField(verbose_name="L. ppm CuSFe", blank=True, null=True)
    l_ppm_bk_cus_fe = models.FloatField(verbose_name="L. ppm-Bk CuSFe", blank=True, null=True)
    cus_fe = models.FloatField(verbose_name="CuSFe (%)", blank=True, null=True)
    control2_cut_cus_fe = models.FloatField(verbose_name="Control2 CuT-CuSFe", blank=True, null=True)
    cut = models.FloatField(verbose_name="CuT", blank=True, null=True)
    cus_c = models.FloatField(verbose_name="CuSC", blank=True, null=True)
    cus_fe_2 = models.FloatField(verbose_name="CuSFe", blank=True, null=True)
    
    def __str__(self):
        return f"Análisis CuS3-CuSFe: {self.elemento}"

class AnalisisCuTestConsH(models.Model):
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='analisis_cutestconsh')
    control1_cut_cutest = models.FloatField(verbose_name="Control1 CuT-CuTest", blank=True, null=True)
    cut = models.FloatField(verbose_name="CuT", blank=True, null=True)
    cut_test = models.FloatField(verbose_name="CuTest", blank=True, null=True)
    gaston_ml = models.FloatField(verbose_name="Gaston mL", blank=True, null=True)
    gasto_bk_ml = models.FloatField(verbose_name="Gasto Bk mL", blank=True, null=True)
    n_naco3 = models.FloatField(verbose_name="N NaCO3", blank=True, null=True)
    alicuota = models.FloatField(verbose_name="Alicuota", blank=True, null=True)
    consumo_h = models.FloatField(verbose_name="Consumo H+", blank=True, null=True)
    
    def __str__(self):
        return f"Análisis CuTest-ConsH: {self.elemento}"

# Modelo para almacenar los resultados
class Resultado(models.Model):
    nb = models.CharField(max_length=100)
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE, related_name='resultados')
    cu_t = models.FloatField(verbose_name="CuT (%)", blank=True, null=True)
    cu_s4 = models.FloatField(verbose_name="CuS4 (%)", blank=True, null=True)
    cu_s10 = models.FloatField(verbose_name="CuS10 (%)", blank=True, null=True)
    mo = models.FloatField(verbose_name="Mo (%)", blank=True, null=True)
    cu_s_fe = models.FloatField(verbose_name="CuSFe (%)", blank=True, null=True)
    fe_t = models.FloatField(verbose_name="FeT (%)", blank=True, null=True)
    zn = models.FloatField(verbose_name="Zn (%)", blank=True, null=True)
    ag = models.FloatField(verbose_name="Ag (g/T)", blank=True, null=True)
    resultado_as = models.FloatField(verbose_name="As (%)", blank=True, null=True)
    pb = models.FloatField(verbose_name="Pb (%)", blank=True, null=True)
    cu_test = models.FloatField(verbose_name="CuTest (%)", blank=True, null=True)
    ext = models.CharField(max_length=255, verbose_name="EXT", blank=True, null=True)
    cons_h = models.FloatField(verbose_name="Cons H+ (Kg/Ton)", blank=True, null=True)
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión", blank=True, null=True)
    
    def __str__(self):
        return f"Resultado {self.nb} de {self.muestra}"

# Modelo para almacenar los parámetros
class Parametro(models.Model):
    nombre = models.CharField(max_length=100)
    valor = models.CharField(max_length=255)
    
    def __str__(self):
        return self.nombre
