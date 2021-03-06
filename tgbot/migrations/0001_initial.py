# Generated by Django 3.2 on 2021-04-28 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=50, null=True, verbose_name='Фамилия')),
                ('username', models.CharField(max_length=50, null=True, verbose_name='Никнейм')),
                ('state', models.IntegerField(choices=[('0', 'Ожидание'), ('1', 'Ввод имени'), ('2', 'Ввод фамилии'), ('3', 'Ввод названия новой игры'), ('4', 'Ввод описания новой игры'), ('5', 'Ввод идентификатора игры'), ('6', 'Ввести пожелания')], default=0)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.chat')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('about', models.TextField(null=True, verbose_name='Описание')),
            ],
        ),
        migrations.CreateModel(
            name='RoomMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.member')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.room')),
            ],
        ),
    ]
