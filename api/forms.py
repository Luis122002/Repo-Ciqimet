from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import CommonPasswordValidator, validate_password
from api import models



class FormODT(forms.ModelForm):
    class Meta:
        model = models.ODT
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FormElements(forms.ModelForm):
    class Meta:
        model = models.Elementos
        fields = '__all__'

class FormAnalisis(forms.ModelForm):
    class Meta:
        model = models.Analisis
        fields = '__all__'