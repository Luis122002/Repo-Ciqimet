from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import CommonPasswordValidator, validate_password
from .models import User, Proyecto, Cliente, Muestra, AnalisisCuTFeZn, AnalisisCuS4FeS4MoS4, AnalisisMulti, AnalisisCuS10FeS10MoS10, AnalisisCuSCuSFe, AnalisisCuTestConsH, Resultado, ODT, MuestraMasificada, Elementos, MetodoAnalisis, Parametros, Estandar, HojaTrabajo, CurvaturaElementos
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
   
    class Meta:
        model = User 
        fields = ('first_name', 'last_name', 'rut', 'username', 'rolname','turno')
     
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(('Este correo electrónico ya está en uso.'))
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            try:
                validate_password(password1, self.instance)
            except forms.ValidationError as error:
                raise forms.ValidationError(error)
            common_validator = CommonPasswordValidator()
            try:
                common_validator.validate(password1)
            except forms.ValidationError:
                raise forms.ValidationError(("La contraseña es demasiado común."))
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(("Las contraseñas no coinciden."))
        return password2
    
    
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'cliente', 'fecha_emision']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'rut', 'direccion', 'telefono', 'email']

class MuestraForm(forms.ModelForm):
    class Meta:
        model = Muestra
        fields = '__all__'

class AnalisisCuTFeZnForm(forms.ModelForm):
    class Meta:
        model = AnalisisCuTFeZn
        fields = ['l_ppm_fe', 'l_ppm_bk_fe', 'fe', 'l_ppm_zn', 'l_ppm_bk_zn', 'zn']

class AnalisisCuS4FeS4MoS4Form(forms.ModelForm):
    class Meta:
        model = AnalisisCuS4FeS4MoS4
        fields = ['control1_cut_cus', 'l_ppm_cus_fe', 'l_ppm_bk_fes4', 'fes4', 'control2_cut_fes4']

class AnalisisMultiForm(forms.ModelForm):
    class Meta:
        model = AnalisisMulti
        fields = [
            'l_ppm_ag', 'l_ppm_ag_bk', 'ag', 'l_ppm_as', 'l_ppm_as_bk', 
            'analisis_as', 'l_ppm_mo', 'l_ppm_mo_bk', 'mo', 'l_ppm_pb', 
            'l_ppm_pb_bk', 'pb', 'l_ppm_cu', 'l_ppm_cu_bk', 'cu'
        ]

class AnalisisCuS10FeS10MoS10Form(forms.ModelForm):
    class Meta:
        model = AnalisisCuS10FeS10MoS10
        fields = ['control_cut_cus', 'cut', 'cus10']

class AnalisisCuSCuSFeForm(forms.ModelForm):
    class Meta:
        model = AnalisisCuSCuSFe
        fields = [
            'l_ppm_cus_fe', 'l_ppm_bk_cus_fe', 'cus_fe', 
            'control2_cut_cus_fe', 'cut', 'cus_c', 'cus_fe_2'
        ]

class AnalisisCuTestConsHForm(forms.ModelForm):
    class Meta:
        model = AnalisisCuTestConsH
        fields = [
            'control1_cut_cutest', 'cut', 'cut_test', 'gaston_ml', 
            'gasto_bk_ml', 'n_naco3', 'alicuota', 'consumo_h'
        ]

class ResultadoForm(forms.ModelForm):
    class Meta:
        model = Resultado
        fields = '__all__'



class ODTForm(forms.ModelForm):
    class Meta:
        model = ODT
        fields = [
            'Fec_Recep', 'Fec_Finalizacion', 'id', 'Prefijo', 'Cliente', 'Proyecto', 
            'Responsable', 'Prioridad', 'TipoMuestra', 'Referencia', 'Comentarios', 'Cant_Muestra'
        ]
        widgets = {
            'Fec_Recep': forms.DateInput(attrs={'type': 'date'}),
            'Fec_Finalizacion': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Fec_Recep'].input_formats = ['%Y-%m-%d']
        self.fields['Fec_Finalizacion'].input_formats = ['%Y-%m-%d']
    

    def save(self, commit=True):
        odt_instance = super().save(commit=commit)
        muestras_generadas = []
        if odt_instance.Prefijo and odt_instance.Cant_Muestra:
            base_prefijo = int(odt_instance.Prefijo)

            for i in range(odt_instance.Cant_Muestra):
                nuevo_prefijo = str(base_prefijo + i)
                muestra_existente = MuestraMasificada.objects.filter(odt=odt_instance, Prefijo=nuevo_prefijo).first()
                if muestra_existente:
                    muestras_generadas.append(muestra_existente)
                else:
                    nueva_muestra = MuestraMasificada.objects.create(
                        odt=odt_instance,
                        Prefijo=nuevo_prefijo,
                        tipoMuestra=odt_instance.TipoMuestra or 'M'
                    )
                    muestras_generadas.append(nueva_muestra)
        todas_muestras_odt = set(MuestraMasificada.objects.filter(odt=odt_instance))
        muestras_sobrantes = todas_muestras_odt - set(muestras_generadas)
        muestras_en_uso = []
        for muestra in muestras_sobrantes:
            if Muestra.objects.filter(muestraMasificada=muestra).exists():
                muestras_en_uso.append(muestra)
        if muestras_en_uso:
            raise ValidationError("Hay muestras que están en hojas de trabajo, primero elimínelas para continuar.")
        muestras_a_eliminar = muestras_sobrantes - set(muestras_en_uso)
        for muestra in muestras_a_eliminar:
            muestra.delete()

        return odt_instance

class MuestraMasificadaForm(forms.ModelForm):
    class Meta:
        model = MuestraMasificada
        fields = ['odt', 'Prefijo', 'tipoMuestra']
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ElementosForm(forms.ModelForm):
    class Meta:
        model = Elementos
        fields = ['nombre', 'gramos', 'miligramos']

class MetodoAnalisisForm(forms.ModelForm):
    class Meta:
        model = MetodoAnalisis
        fields = ['cliente', 'nombre', 'metodologia', 'elementos']
        widgets = {
            'metodologia': forms.Textarea(attrs={'rows': 4}),
        }

class ParametrosForm(forms.ModelForm):
    class Meta:
        model = Parametros
        fields = ['Elementos', 'Unidad', 'VA', 'DS', 'Min', 'Max']
        widgets = {
            'Elementos': forms.CheckboxSelectMultiple,
        }

class EstandarForm(forms.ModelForm):
    class Meta:
        model = Estandar
        fields = ['Nombre', 'cliente', 'parametros']
        widgets = {
            'parametros': forms.CheckboxSelectMultiple,
        }

class HojaTrabajoForm(forms.ModelForm):
    class Meta:
        model = HojaTrabajo
        fields = ['odt', 'Estandar', 'MetodoAnalisis', 'MuestraMasificada', 'Tipo', 'Duplicado']
        widgets = {
            'Estandar': forms.CheckboxSelectMultiple,
            'Tipo': forms.Select(choices=[('M', 'Muestra'), ('S', 'Estandar'), ('D', 'Duplicado'), ('B', 'Blanco')]),
        }


class HojaTrabajoGeneralForm(forms.ModelForm):
    class Meta:
        model = HojaTrabajo
        fields = ['ID_HDT', 'odt', 'Estandar', 'MetodoAnalisis', 'Tipo', 'Duplicado']
        widgets = {
            'Estandar': forms.CheckboxSelectMultiple,
            'Tipo': forms.Select(choices=[('M', 'Muestra'), ('S', 'Estandar'), ('D', 'Duplicado'), ('B', 'Blanco')]),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        id_hdt_value = self.cleaned_data['ID_HDT']
        odt = self.cleaned_data['odt']
        metodo_analisis = instance.MetodoAnalisis
        muestras = MuestraMasificada.objects.filter(odt=odt)
        
        hojas_trabajo = []
        count = 0
        
        elementos = metodo_analisis.elementos.all()
        
        for muestra in muestras:
            # Crear la hoja de trabajo para cada muestra
            if count == 0:
                hoja_trabajo = instance
                hoja_trabajo.MuestraMasificada = muestra
                hoja_trabajo.save()  # Guarda la primera hoja de trabajo
            else:
                hoja_trabajo = HojaTrabajo(
                    ID_HDT=id_hdt_value,
                    odt=odt,
                    MetodoAnalisis=instance.MetodoAnalisis,
                    Tipo=instance.Tipo,
                    Duplicado=instance.Duplicado,
                    MuestraMasificada=muestra
                )
                hoja_trabajo.save()  # Guarda la hoja de trabajo
                hoja_trabajo.Estandar.set(self.cleaned_data['Estandar'])  # Establece los valores de 'Estandar'
            
            hojas_trabajo.append(hoja_trabajo)
            count += 1

            for elemento in elementos:
                curvatura = CurvaturaElementos.objects.filter(
                    cliente=metodo_analisis.cliente,
                    elemento=elemento
                ).first()
                
                curvatura_valor = curvatura.curvatura if curvatura else 1
                print(f"Elemento: {elemento.nombre} - Curvatura: {curvatura_valor}")
                
                for index in range(1, curvatura_valor + 1):
                    muestra_instance = Muestra(
                        nombre=f"{elemento.nombre} - Muestra {index}",
                        proyecto=odt.Proyecto,
                        fecha_emision=timezone.now(),
                        elemento=elemento.nombre,
                        nbo=f"NBO-{index}", 
                        ident=f"ID-{index}",
                        indexCurv=index,
                        hoja_trabajo=hoja_trabajo,  
                        muestraMasificada=muestra,
                        t="M", 
                        peso_m=0.0, 
                        v_ml=0.0, 
                        l_ppm=0.0, 
                        l_ppm_bk=0.0,  
                        porcentaje=0.0  
                    )
                    muestra_instance.save() 

                resultado_instance = Resultado(
                    elemento=elemento, 
                    muestra=muestra, 
                    hoja_trabajo=hoja_trabajo,
                    resultadoAnalisis=0, 
                    fecha_emision=timezone.now()
                )
                resultado_instance.save() 

        if commit:
            instance.save()
        
        return instance
    
class CurvaturaForm(forms.ModelForm):
    class Meta:
        model = CurvaturaElementos
        fields = '__all__'