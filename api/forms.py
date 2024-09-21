from django import forms
from api import models

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
        exclude = ['Cant_Muestra']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-General',
                'data-bs-toggle': 'tooltip',
                'title': field.help_text
            })

        self.fields['Nro_OT'].help_text = 'Número de orden de trabajo, por ejemplo: OT123456.'
        self.fields['Fec_Recep'].help_text = 'Fecha de recepción de la muestra.'
        self.fields['Cliente'].help_text = 'Seleccione el cliente que solicita la muestra.'
        self.fields['Proyecto'].help_text = 'Nombre del proyecto al que se asigna la muestra.'
        self.fields['Despacho'].help_text = 'Sección donde se entrega la orden de trabajo.'
        self.fields['Envio'].help_text = 'Seleccione el usuario responsable del envío.'
        self.fields['Muestra'].help_text = 'Código de identificación de la muestra.'
        self.fields['Comentarios'].help_text = 'Comentarios adicionales sobre la muestra, si los hay.'
        self.fields['InicioCodigo'].help_text = 'Número de inicio para el código de muestra (1-999).'
        self.fields['FinCodigo'].help_text = 'Número final para el código de muestra (1-999).'

        # Bloquear campos si se está modificando un registro existente
        if self.instance.pk:  # Si ya tiene un ID, es una modificación
            self.fields['InicioCodigo'].widget.attrs['readonly'] = 'readonly'
            self.fields['FinCodigo'].widget.attrs['readonly'] = 'readonly'
            self.fields['InicioCodigo'].widget.attrs['style'] = 'background-color: #f0f0f0; cursor: not-allowed;'
            self.fields['FinCodigo'].widget.attrs['style'] = 'background-color: #f0f0f0; cursor: not-allowed;'
        
        # Asegurarse de que la fecha de recepción tenga el formato correcto
        if 'Fec_Recep' in self.data:
            self.fields['Fec_Recep'].widget.attrs['value'] = self.data['Fec_Recep']
        elif self.instance and self.instance.Fec_Recep:
            self.fields['Fec_Recep'].widget.attrs['value'] = self.instance.Fec_Recep.strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        inicio_codigo = cleaned_data.get('InicioCodigo')
        fin_codigo = cleaned_data.get('FinCodigo')
        muestra_codigo = cleaned_data.get('Muestra')

        # Solo aplicar validaciones si es un nuevo registro
        if not self.instance.pk:  # Si no tiene un ID, es un nuevo registro
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