# Generated by Django 3.2 on 2021-04-28 15:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.room'),
        ),
        migrations.AlterField(
            model_name='member',
            name='state',
            field=models.IntegerField(choices=[('0', 'Ожидание'), ('1', 'Ввод имени'), ('2', 'Ввод фамилии'), ('3', 'Ввод названия новой игры'), ('4', 'Ввод описания новой игры'), ('5', 'Ввод идентификатора игры'), ('6', 'Ввод пожеланий'), ('7', 'Ввод идентификатора комнаты')], default=0),
        ),
        migrations.AlterField(
            model_name='room',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
