# Generated by Django 5.0.4 on 2024-09-16 05:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_odt_proyecto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='odt',
            name='Cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.cliente'),
        ),
    ]