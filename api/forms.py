from django import forms
from api import models
import uuid
from datetime import datetime
import random

class FormODT(forms.ModelForm):
    class Meta:
        model = models.ODT
        fields = '__all__'
        widgets = {
            'Fec_Recep': forms.DateInput(attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd'}),
            'Comentarios': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ingrese comentarios adicionales'}),
            'InicioCodigo': forms.NumberInput(attrs={'max': 999, 'min': 1, 'placeholder': 'Ej. 101'}),
            'FinCodigo': forms.NumberInput(attrs={'max': 999, 'min': 1, 'placeholder': 'Ej. 201'}),
            'Despacho': forms.TextInput(attrs={'placeholder': 'Ej. CG-12345678'}),
            
            'Nro_OT': forms.TextInput(attrs={'placeholder': 'Ej. OT123456'}),
            'Muestra': forms.TextInput(attrs={'placeholder': 'Código de identificación de muestra'}),
        }
        exclude = ['Cant_Muestra']  # Ocultar cliente en el formulario

    def __init__(self, *args, **kwargs):
        # Capturamos el proyecto desde los kwargs si está disponible
        self.proyecto = kwargs.pop('proyecto', None)
        super().__init__(*args, **kwargs)

        # Si es un nuevo registro (sin pk), genera automáticamente Nro_OT y Muestra
        if not self.instance.pk:
            self.fields['Nro_OT'].initial = self.generar_nro_ot()
            self.fields['Muestra'].initial = self.generar_codigo_muestra()


        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-General',
                'data-bs-toggle': 'tooltip',
                'title': field.help_text
            })

        # Asegurarse de que la fecha de recepción tenga el formato correcto
        if 'Fec_Recep' in self.data:
            self.fields['Fec_Recep'].widget.attrs['value'] = self.data['Fec_Recep']
        elif self.instance and self.instance.Fec_Recep:
            self.fields['Fec_Recep'].widget.attrs['value'] = self.instance.Fec_Recep.strftime('%Y-%m-%d')

    def generar_nro_ot(self):
        # Número único basado en la fecha y un valor aleatorio
        fecha_actual = datetime.now().strftime('%Y%m%d%H%M%S')
        numero_aleatorio = random.randint(100, 999)
        return f"OT{fecha_actual}{numero_aleatorio}"

    def generar_codigo_muestra(self):
        # Código único basado en UUID acortado
        return f"M-{uuid.uuid4().hex[:8]}"

    def clean(self):
        cleaned_data = super().clean()
        inicio_codigo = cleaned_data.get('InicioCodigo')
        fin_codigo = cleaned_data.get('FinCodigo')
        muestra_codigo = cleaned_data.get('Muestra')
        

        # Validación del rango de códigos
        if not self.instance.pk:
            if inicio_codigo is not None and fin_codigo is not None:
                if fin_codigo < inicio_codigo:
                    self.add_error('FinCodigo', 'El número final del código debe ser mayor o igual al número inicial.')

                for codigo in range(inicio_codigo, fin_codigo + 1):
                    codigo_completo = f"{muestra_codigo}-{codigo:02d}"
                    if models.OT.objects.filter(id_muestra=codigo_completo).exists():
                        self.add_error(None, f'El código de muestra {codigo_completo} ya existe en OT.')

        return cleaned_data
    

class FormElements(forms.ModelForm):
    class Meta:
        model = models.Elementos
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción opcional del elemento'}),
            'simbolo': forms.TextInput(attrs={'maxlength': 5, 'placeholder': 'Ej. H'}),
            'numero_atomico': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Ej. 1'}),
            'masa_atomica': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Ej. 1.008'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-General'})

        self.fields['nombre'].help_text = 'Nombre del elemento, por ejemplo: Hidrógeno.'
        self.fields['descripcion'].help_text = 'Descripción opcional del elemento. Máximo 255 caracteres.'
        self.fields['tipo'].help_text = 'Tipo de elemento, por ejemplo: Metal, No metal.'
        self.fields['enabled'].help_text = 'Marque si el elemento está activo.'
        self.fields['simbolo'].help_text = 'Símbolo químico del elemento, por ejemplo: H, O.'
        self.fields['numero_atomico'].help_text = 'Número atómico del elemento, por ejemplo: 1 para Hidrógeno.'
        self.fields['masa_atomica'].help_text = 'Masa atómica del elemento en unidades de masa atómica (uma).'

class FormAnalisis(forms.ModelForm):
    class Meta:
        model = models.Analisis
        fields = '__all__'
        widgets = {
            'Analisis_metodo': forms.TextInput(attrs={'placeholder': 'Ej. Análisis de espectroscopía de masas'}),
            'Nro_Analisis': forms.TextInput(attrs={'placeholder': 'Ej. MA-001'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción del análisis metalúrgico'}),
            'Formula': forms.TextInput(attrs={'placeholder': 'Ej. Fe, Al, Cu'}),
            'Elementos': forms.SelectMultiple(attrs={'class': 'form-General'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-General'})

        self.fields['Analisis_metodo'].help_text = 'Método de análisis metalúrgico, por ejemplo: Análisis de espectroscopía de masas.'
        self.fields['Nro_Analisis'].help_text = 'Código único para el análisis, por ejemplo: MA-001.'
        self.fields['descripcion'].help_text = 'Descripción del análisis metalúrgico. Máximo 255 caracteres.'
        self.fields['Formula'].help_text = 'Fórmulas de los elementos metalúrgicos analizados, por ejemplo: Fe, Al, Cu.'
        self.fields['Elementos'].help_text = 'Seleccione los elementos metalúrgicos involucrados en el análisis.'
        self.fields['enabled'].help_text = 'Marque si el análisis está activo.'