# Generated by Django 5.1.4 on 2025-01-25 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0011_customuser_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
