# Generated by Django 3.2 on 2021-05-02 12:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0005_auto_20210502_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='created',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
