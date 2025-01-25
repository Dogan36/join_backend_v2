# Generated by Django 5.1.4 on 2025-01-25 18:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colors', '0001_initial'),
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='colors.color'),
        ),
        migrations.DeleteModel(
            name='Color',
        ),
    ]
