# Generated by Django 5.0.4 on 2024-11-14 16:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Novedades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_model', models.CharField(choices=[('Orden_de_trabajo', 'Orden de trabajo'), ('Hoja_de_trabajo', 'Hoja de trabajo')], max_length=200)),
                ('accion', models.CharField(choices=[('Crear', 'Crear'), ('Modificar', 'Modificar'), ('Eliminar', 'Eliminar'), ('Balanza', 'Balanza'), ('Absorcion', 'Absorción')], max_length=200)),
                ('modelt_id', models.CharField(max_length=200, verbose_name='ID registro')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'Novedades',
            },
        ),
        migrations.AlterField(
            model_name='hojatrabajoquimico',
            name='HojaTrabajo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hojas_trabajo_target', to='api.hojatrabajo'),
        ),
    ]
