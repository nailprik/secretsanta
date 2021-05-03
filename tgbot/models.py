import uuid

from django.db import models
from django.utils import timezone


class Chat(models.Model):
    id = models.IntegerField(primary_key=True)


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', null=True)
    is_started = models.BooleanField(default=False)
    created = models.DateField(default=timezone.now)



class Member(models.Model):
    STATE_CHOICES = [
        (0,'Ожидание'),
        (1,'Ввод имени'),
        (2, 'Ввод фамилии'),
        (3, 'Ввод названия новой комнаты'),
        (4, 'Ввод описания новой комнаты'),
        (5, 'Ввод идентификатора комнаты'),
        (6, 'Ввод пожеланий'),
        (7, 'Ввод названия комнаты'),
        (8, 'Ввод описания комнаты')
    ]
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия', null=True)
    username = models.CharField(max_length=50, verbose_name='Никнейм', blank=True, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    state = models.IntegerField(choices=STATE_CHOICES, default=0)
    last_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)


class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_member')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, related_name='receiver')
    wish = models.TextField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

