from django.contrib import admin
from .models import (
    User, Proyecto, Cliente, Muestra, AnalisisCuTFeZn, AnalisisCuS4FeS4MoS4, AnalisisMulti,
    AnalisisCuS10FeS10MoS10, AnalisisCuSCuSFe, AnalisisCuTestConsH, Resultado, ODT, MuestraMasificada,
    Elementos, MetodoAnalisis, Parametros, Estandar, HojaTrabajo, HojaTrabajoQuimico, CurvaturaElementos
)
from .forms import (
    CustomUserCreationForm, ProyectoForm, ClienteForm, MuestraForm, AnalisisCuTFeZnForm,
    AnalisisCuS4FeS4MoS4Form, AnalisisMultiForm, AnalisisCuS10FeS10MoS10Form, AnalisisCuSCuSFeForm,
    AnalisisCuTestConsHForm, ResultadoForm, ODTForm, MuestraMasificadaForm, ElementosForm,
    MetodoAnalisisForm, ParametrosForm, EstandarForm, HojaTrabajoForm, HojaTrabajoGeneralForm, HojaTrabajoQuimicoForm,  CurvaturaForm
)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm
    list_display = ('username', 'first_name', 'last_name', 'rolname', 'turno')


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    form = ProyectoForm
    list_display = ('nombre', 'cliente', 'fecha_emision')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteForm
    list_display = ('nombre', 'rut', 'direccion', 'telefono', 'email')





@admin.register(AnalisisCuTFeZn)
class AnalisisCuTFeZnAdmin(admin.ModelAdmin):
    form = AnalisisCuTFeZnForm
    list_display = ('l_ppm_fe', 'l_ppm_bk_fe', 'fe', 'l_ppm_zn', 'l_ppm_bk_zn', 'zn')


@admin.register(AnalisisCuS4FeS4MoS4)
class AnalisisCuS4FeS4MoS4Admin(admin.ModelAdmin):
    form = AnalisisCuS4FeS4MoS4Form
    list_display = ('control1_cut_cus', 'l_ppm_cus_fe', 'fes4', 'control2_cut_fes4')


@admin.register(AnalisisMulti)
class AnalisisMultiAdmin(admin.ModelAdmin):
    form = AnalisisMultiForm
    list_display = ('l_ppm_ag', 'l_ppm_as', 'l_ppm_mo', 'l_ppm_pb', 'l_ppm_cu')


@admin.register(AnalisisCuS10FeS10MoS10)
class AnalisisCuS10FeS10MoS10Admin(admin.ModelAdmin):
    form = AnalisisCuS10FeS10MoS10Form
    list_display = ('control_cut_cus', 'cut', 'cus10')


@admin.register(AnalisisCuSCuSFe)
class AnalisisCuSCuSFeAdmin(admin.ModelAdmin):
    form = AnalisisCuSCuSFeForm
    list_display = ('l_ppm_cus_fe', 'cus_fe', 'cut')


@admin.register(AnalisisCuTestConsH)
class AnalisisCuTestConsHAdmin(admin.ModelAdmin):
    form = AnalisisCuTestConsHForm
    list_display = ('control1_cut_cutest', 'cut', 'cut_test', 'gaston_ml')


@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    form = ResultadoForm
    list_display = ('elemento', 'muestra', 'hoja_trabajo', 'hoja_trabajo', 'resultadoAnalisis', 'fecha_emision')


@admin.register(ODT)
class ODTAdmin(admin.ModelAdmin):
    form = ODTForm
    list_display = ('Fec_Recep', 'Fec_Finalizacion', 'id', 'Cliente', 'Proyecto', 'Prioridad', 'TipoMuestra')


@admin.register(MuestraMasificada)
class MuestraMasificadaAdmin(admin.ModelAdmin):
    form = MuestraMasificadaForm
    list_display = ('odt', 'Prefijo', 'tipoMuestra', 'fecha_creacion')

@admin.register(Muestra)
class MuestrasAdmin(admin.ModelAdmin):
    form = MuestraForm
    list_display = ('nombre', 'proyecto', 'fecha_emision', 'elemento', 'nbo', 'ident', 'indexCurv', 't', 'peso_m', 'v_ml', 'l_ppm', 'l_ppm_bk', 'porcentaje')


@admin.register(Elementos)
class ElementosAdmin(admin.ModelAdmin):
    
    form = ElementosForm
    list_display = ('nombre', 'gramos', 'miligramos')


@admin.register(MetodoAnalisis)
class MetodoAnalisisAdmin(admin.ModelAdmin):
    form = MetodoAnalisisForm
    list_display = ('cliente', 'nombre')


@admin.register(Parametros)
class ParametrosAdmin(admin.ModelAdmin):
    form = ParametrosForm
    list_display = ('Unidad', 'VA', 'DS', 'Min', 'Max')


@admin.register(Estandar)
class EstandarAdmin(admin.ModelAdmin):
    form = EstandarForm
    list_display = ('Nombre', 'cliente')


@admin.register(HojaTrabajo)
class HojaTrabajoAdmin(admin.ModelAdmin):
    form = HojaTrabajoGeneralForm
    list_display = ('odt', 'MetodoAnalisis', 'Tipo')


@admin.register(HojaTrabajoQuimico)
class HojaTrabajoQuimicosAdmin(admin.ModelAdmin):
    form = HojaTrabajoQuimicoForm
    list_display = ('ID_HDT', 'confirmar_balanza', 'confirmar_Absorcion', 'HojaTrabajo')

@admin.register(CurvaturaElementos)
class CurvaturaAdmin(admin.ModelAdmin):
    form = CurvaturaForm
    list_display = ('cliente','elemento', 'curvatura')