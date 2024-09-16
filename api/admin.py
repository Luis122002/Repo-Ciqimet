from django.contrib import admin
from .models import User, Cliente, Proyecto, ODT, Analisis, Elementos, OT, LecturasElementos

# Registrar el modelo User (si no lo has hecho ya)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class UserCreationFormCustom(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

class UserChangeFormCustom(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class UserAdmin(BaseUserAdmin):
    form = UserChangeFormCustom
    add_form = UserCreationFormCustom
    list_display = ('username', 'email', 'rolname', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'rolname')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'rolname')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'rolname'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, UserAdmin)

# Registrar los modelos Cliente y Proyecto
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre_cliente')
    search_fields = ('user__username', 'nombre_cliente')

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente')
    search_fields = ('nombre', 'cliente__user__username')
    list_filter = ('cliente',)

# Registrar otros modelos si es necesario
@admin.register(ODT)
class ODTAdmin(admin.ModelAdmin):
    list_display = ('Nro_OT', 'Fec_Recep', 'Cliente', 'Proyecto', 'Despacho', 'Envio', 'Muestra', 'Referencia', 'Comentarios', 'InicioCodigo', 'FinCodigo', 'Cant_Muestra', 'Turno')
    search_fields = ('Nro_OT', 'Muestra', 'Referencia', 'Cliente__username', 'Proyecto')
    list_filter = ('Cliente', 'Turno')

@admin.register(Analisis)
class AnalisisAdmin(admin.ModelAdmin):
    list_display = ('Analisis_metodo', 'descripcion', 'Formula')
    search_fields = ('Analisis_metodo', 'descripcion')

@admin.register(Elementos)
class ElementosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'tipo', 'enabled', 'simbolo', 'numero_atomico', 'masa_atomica')
    search_fields = ('nombre', 'tipo', 'descripcion')

@admin.register(OT)
class OTAdmin(admin.ModelAdmin):
    list_display = ('id_muestra', 'peso_muestra', 'volumen', 'dilucion', 'odt', 'analisis', 'Elemento')
    search_fields = ('id_muestra', 'odt__Nro_OT', 'analisis__Analisis_metodo', 'Elemento__nombre')

@admin.register(LecturasElementos)
class LecturasElementosAdmin(admin.ModelAdmin):
    list_display = ('lectura', 'analisis', 'ot', 'elementos')
    search_fields = ('analisis__Analisis_metodo', 'ot__id_muestra', 'elementos__nombre')