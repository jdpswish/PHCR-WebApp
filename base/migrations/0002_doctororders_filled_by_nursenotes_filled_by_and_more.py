# Generated by Django 5.0.4 on 2024-04-27 13:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctororders',
            name='filled_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filled_doctor_orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='nursenotes',
            name='filled_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filled_nurse_notes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vitalsigns',
            name='filled_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filled_vital_signs', to=settings.AUTH_USER_MODEL),
        ),
    ]
