# Generated by Django 5.0.4 on 2024-09-09 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_odt_cant_muestra'),
    ]

    operations = [
        migrations.AlterField(
            model_name='odt',
            name='Muestra',
            field=models.CharField(max_length=200, verbose_name='Código de muestras'),
        ),
    ]
