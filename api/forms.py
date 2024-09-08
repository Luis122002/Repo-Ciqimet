from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import CommonPasswordValidator, validate_password
from api import models



class FormODT(forms.ModelForm):
    class Meta:
        model = models.ODT
        fields = '__all__'
        widgets = {
            'Fec_Recep': forms.DateInput(attrs={'type': 'date'}),
            'Comentarios': forms.Textarea(attrs={'rows': 3}),
            'InicioCodigo': forms.NumberInput(attrs={'max': 99999, 'min': 1}),
            'FinCodigo': forms.NumberInput(attrs={'max': 99999, 'min': 1}),
        }
        exclude = ['Cant_Muestra']  # Excluir Cant_Muestra de los campos editables

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Nro_OT'].help_text = 'Número de orden de trabajo, por ejemplo: OT123456.'
        self.fields['Fec_Recep'].help_text = 'Fecha de recepción de la muestra.'
        self.fields['Cliente'].help_text = 'Nombre del cliente que solicita la muestra.'
        self.fields['Proyecto'].help_text = 'Nombre del proyecto al que se asigna la muestra.'
        self.fields['Despacho'].help_text = 'Detalles del despacho relacionado con la muestra.'
        self.fields['Envio'].help_text = 'Detalles del envío relacionado con la muestra.'
        self.fields['Muestra'].help_text = 'Código de identificación de la muestra.'
        self.fields['Referencia'].help_text = 'Referencia adicional relacionada con la muestra.'
        self.fields['Comentarios'].help_text = 'Comentarios adicionales sobre la muestra, si los hay.'
        self.fields['InicioCodigo'].help_text = 'Número de inicio para el código de muestra.'
        self.fields['FinCodigo'].help_text = 'Número final para el código de muestra.'

    def clean(self):
        cleaned_data = super().clean()
        inicio_codigo = cleaned_data.get('InicioCodigo')
        fin_codigo = cleaned_data.get('FinCodigo')

        if inicio_codigo is not None and fin_codigo is not None:
            if fin_codigo < inicio_codigo:
                self.add_error('FinCodigo', 'El número final del código debe ser mayor o igual al número inicial.')

        return cleaned_data


class FormElements(forms.ModelForm):
    class Meta:
        model = models.Elementos
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'simbolo': forms.TextInput(attrs={'maxlength': 5}),
            'numero_atomico': forms.NumberInput(attrs={'min': 1}),
            'masa_atomica': forms.NumberInput(attrs={'step': 'any'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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