import json
import random

import requests
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import JsonResponse

from secretsanta.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN, BASE_URL
from tgbot.models import Chat, Member, Room, RoomMember
from tgbot.tasks import edit_message, send_message, mailing


def set_webhook():
    url = f"{BASE_URL}/bot{TELEGRAM_BOT_TOKEN}/"
    data = {
        "url": url,
        "allowed_updates": ["message","callback_query"]
    }
    response = requests.post(f"{TELEGRAM_URL}/bot{TELEGRAM_BOT_TOKEN}/setWebhook", data=data)
    print(response.content)
    return response.content


def message_handler(message):
    chat_data = message["chat"]
    (chat, created) = Chat.objects.get_or_create(id=chat_data['id'])
    (member, created) = Member.objects.get_or_create(chat=chat)
    if created:
        member.state = 1
        answer = "Здравствуйте, введите ваше имя"
        member.save()
    elif member.state == 1:
        if message["text"].isalpha():
            member.first_name = message["text"]
            member.state = 2
            answer = "Введите фамилию"
            member.save()
        else:
            answer = "Введите корректное имя (используйте только буквы)"
    elif member.state == 2:
        if message["text"].isalpha():
            member.last_name = message["text"]
            member.state = 0
            answer = "Теперь вы можете создать или присоединиться к новой игре. Доступные команды вы можете " \
                     "посмотреть отправив /help "
            member.save()
            send_message.delay(answer, chat.id)
        else:
            answer = "Введите корректную фамилию"
    elif member.state == 3:
        if not message["text"].startswith('/'):
            current_room = Room.objects.create(name=message["text"])
            RoomMember.objects.create(member=member, room=current_room, is_admin=True)
            member.last_room = current_room
            member.state = 4
            answer = "Введите описание комнаты"
            member.save()
        else:
            answer = "Недопустимо начинать название с символа '/'. Введите корректное название"
    elif member.state == 4:
        if not message["text"].startswith('/'):
            current_room = member.last_room
            current_room.description = message["text"]
            member.state = 0
            member.save()
            current_room.save()
            answer = f"Комната создана.\nНазвание: *{current_room.name}*\nОписание: *{current_room.description}*\n" \
                     f"Идентификатор:\n`{current_room.id}`\nПришлите этот идентификатор другим участникам для " \
                     f"подключения "
        else:
            answer = "Недопустимо начинать описание с символа '/'. Введите корректное описание"
    elif member.state == 5:
        if not message["text"].startswith('/'):
            try:
                current_room = Room.objects.get(id=message["text"])
            except (ValidationError, ObjectDoesNotExist):
                current_room = None
            if current_room:
                (relation, created) = RoomMember.objects.get_or_create(member=member, room=current_room)
                if created:
                    answer = f"Вы подключились к комнате.\nНазвание: *{current_room.name}*\nОписание: *{current_room.description}*\nИдентификатор:\n`{current_room.id}`\nКогда создатель комнаты начнет игру, вы получите в сообщении информацию о том, кому вы будете дарить подарок и его пожелания."
                else:
                    answer = "Вы уже подключены к этой комнате. Когда создатель комнаты начнет игру, вы получите в " \
                             "сообщении информацию о том, кому вы будете дарить и его пожелания. "
            else:
                answer = "Комната с таким идентификатором не найдена. Попробуйте еще раз или создайте свою игру"
            member.state = 0
            member.save()
        else:
            answer = "Комната с таким идентификатором не найдена. Попробуйте еще раз или создайте свою игру"
    elif member.state == 6:
        if not message["text"].startswith('/'):
            current_room = member.last_room
            member.state = 0
            member.save()
            try:
                room_member = RoomMember.objects.get(member=member, room=current_room)
                room_member.wish = message["text"]
                room_member.save()
                answer = 'Ваше пожелание сохранено'
            except ObjectDoesNotExist:
                answer = 'Произошла ошибка, попробуйте позже'
        else:
            answer = "Недопустимо начинать пожелание с символа '/'. Введите корректное пожелание"
    elif member.state == 7:
        if not message["text"].startswith('/'):
            current_room = member.last_room
            current_room.name = message["text"]
            member.state = 0
            answer = f"Новое название комнаты:*{current_room.name}*"
            member.save()
            current_room.save()
        else:
            answer = "Недопустимо начинать название с символа '/'. Введите корректное название"
    elif member.state == 8:
        if not message["text"].startswith('/'):
            current_room = member.last_room
            current_room.description = message["text"]
            member.state = 0
            answer = f"Новое описание комнаты:*{current_room.description}*"
            member.save()
            current_room.save()
        else:
            answer = "Недопустимо начинать описание с символа '/'. Введите корректное название"
    elif member.state == 0:
        if message["text"].startswith('/'):
            command = message["text"]
            if command == '/newgame':#TODO может сделать кнопками
                member.state = 3
                answer = "Введите название комнаты"
                send_message.delay(answer, chat.id)
                member.save()
                return JsonResponse({"ok": "POST request processed"})
            elif command == '/connect':#TODO тоже кнопками
                member.state = 5
                answer = "Введите идентификатор комнаты"
                send_message.delay(answer, chat.id)
                member.save()
                return JsonResponse({"ok": "POST request processed"})
            elif command == '/list':#TODO Добавить функционал списка участников в майрумс
                answer = "Введите идентификатор комнаты"
                send_message.delay(answer, chat.id)
                return JsonResponse({"ok": "POST request processed"})
            elif command == '/myrooms':
                rooms = Room.objects.filter(room_member__member=member).values_list('id','name')
                if rooms:
                    answer = "Выберите комнату:"
                    reply_markup = json.dumps(
                        {"inline_keyboard": [[{"text": name, "callback_data": str(uid)}] for (uid, name) in rooms]})
                    send_message.delay(answer, chat.id, reply_markup)
                else:
                    answer = "Вы не участвуете ни в одной игре. Создайте свою!"
                    send_message.delay(answer, chat.id)
                return JsonResponse({"ok": "POST request processed"})
            elif command == '/help':
                answer = "/newgame - Создание новой комнаты\n/connect - присодединиться к существующей игре\n/myrooms- список моих комнат\n"
                send_message.delay(answer, chat.id)
                return JsonResponse({"ok": "POST request processed"})
            else:
                answer = "Неизвестная команда. Доступные команды вы можете посмотреть отправив /help"
                send_message.delay(answer, chat.id)
                return JsonResponse({"ok": "POST request processed"})
        else:#TODO Кажется повторение ниже
            answer = "Вы можете создать или присоединиться к новой игре. Доступные команды вы можете посмотреть отправив /help"
    else:
        answer = "Вы можете создать или присоединиться к новой игре. Доступные команды вы можете посмотреть отправив /help"
    send_message.delay(answer, chat.id)
    return JsonResponse({"ok": "POST request processed"})


def callback_handler(callback_query):
    message = callback_query["message"]
    chat_data = message["chat"]
    chat = Chat.objects.get(id=chat_data['id'])
    member= Member.objects.get(chat=chat)
    data = callback_query.get('data')
    inline_keyboard = []
    if data:
        try:
            current_room = Room.objects.get(id=data)
        except (ValidationError, ObjectDoesNotExist):
            current_room = None
        if current_room:
            answer = f"Выбрана комната {current_room.name} с идентификатором\n`{current_room.id}`\n Что вы хотите сделать?"
            member.last_room = current_room
            member.save()
            room_member = RoomMember.objects.get(room=current_room, member=member)
            if room_member.is_admin:
                if not current_room.is_started:
                    start_room_btn = [{'text': 'Начать игру', 'callback_data': 'start_room'}]
                else:
                    start_room_btn = []
                edit_room_name_btn = [{'text': 'Изменить название', 'callback_data': 'edit_room_name'}]
                edit_room_description_btn = [{'text': 'Изменить описание', 'callback_data': 'edit_room_description'}]
                delete_room_btn = [{'text': 'Удалить', 'callback_data': 'delete_room'}]
                inline_keyboard = [start_room_btn, edit_room_name_btn, edit_room_description_btn, delete_room_btn]
            if not current_room.is_started:
                exit_room_btn = [{'text': 'Покинтуть комнату', 'callback_data': 'exit_room'}]
                inline_keyboard.append(exit_room_btn)
            else:
                watch_receiver_btn = [{'text': 'Инфо о получателе', 'callback_data': 'watch_receiver'}]
                inline_keyboard.append(watch_receiver_btn)
            edit_wish_btn = [{'text': 'Изменить пожелание', 'callback_data': 'edit_wish'}]
            inline_keyboard.append(edit_wish_btn)
        elif data == 'start_room':
            current_room = member.last_room
            try:
                room_member = RoomMember.objects.get(room=current_room, member=member, is_admin=True)
                member_count = RoomMember.objects.filter(room=current_room).count()
                if member_count < 2:
                    answer = "Вы не можете начать игру с одним участником"
                else:
                    answer = f"Вы уверены, что хотите начть игру? Количество участников: {member_count}"
                    accept_btn = [{'text': 'Да', 'callback_data': 'accept_start'}]
                    decline_btn = [{'text': 'Отмена', 'callback_data': 'decline_start'}]
                    inline_keyboard.append(accept_btn)
                    inline_keyboard.append(decline_btn)
            except ObjectDoesNotExist:
                answer = 'Вы не являетесь админом этой комнаты!'
        elif data == 'edit_room_name':
            member.state = 7
            answer = "Введите название комнаты"
            member.save()
        elif data == 'edit_room_description':
            member.state = 8
            answer = "Введите описание комнаты"
            member.save()
        elif data == "accept_start":
            current_room = member.last_room
            current_room.is_started = True
            current_room.save()
            member_list = list(RoomMember.objects.filter(room=current_room))
            random.shuffle(member_list)
            answer = ''
            for i in range(len(member_list) - 1, -1, -1):
                member_list[i].receiver = member_list[i-1].member
                member_list[i].save()
                answer += f'{member_list[i].member.first_name} -> {member_list[i].receiver.first_name}\n'
            answer = f'Игра комнаты {current_room.name} с идентификатором\n`{current_room.id}`\nначалась!' \
            'Скоро вам придет сообщение с информацией о получателе. Если сообщение не придет, вы можете посмотреть получателя в инофрмации о комнате'
            recipients = [room_member.member.chat.id for room_member in member_list]
            mailing.delay(answer, recipients)
            send_message.delay(answer, chat.id)
            return JsonResponse({"ok": "POST request processed"})
        elif data == "decline_start": #TODO исправить повторение кода
            current_room = member.last_room
            answer = f"Выбрана комната *{current_room.name}* с идентификатором\n`{current_room.id}`\n Что вы хотите сделать?"
            member.last_room = current_room
            member.save()
            room_member = RoomMember.objects.get(room=current_room, member=member)
            if room_member.is_admin:
                if not current_room.is_started:
                    start_room_btn = [{'text': 'Начать игру', 'callback_data': 'start_room'}]
                else:
                    start_room_btn = []
                edit_room_name_btn = [{'text': 'Изменить название', 'callback_data': 'edit_room_name'}]
                edit_room_description_btn = [{'text': 'Изменить описание', 'callback_data': 'edit_room_description'}]
                delete_room_btn = [{'text': 'Удалить', 'callback_data': 'delete_room'}]
                inline_keyboard = [start_room_btn, edit_room_name_btn, edit_room_description_btn, delete_room_btn]
            if not current_room.is_started:
                exit_room_btn = [{'text': 'Покинтуть комнату', 'callback_data': 'exit_room'}]
                inline_keyboard.append(exit_room_btn)
            edit_wish_btn = [{'text': 'Изменить пожелание', 'callback_data': 'edit_wish'}]
            watch_receiver_btn = [{'text': 'Инфо о получателе', 'callback_data': 'watch_receiver'}]
            inline_keyboard.append(edit_wish_btn)
            inline_keyboard.append(watch_receiver_btn)
        elif data == 'exit_room':
            answer = f"Вы уверены, что хотите покинуть комнату?"
            accept_btn = [{'text': 'Да', 'callback_data': 'accept_exit'}]
            decline_btn = [{'text': 'Отмена', 'callback_data': 'decline_exit'}]
            inline_keyboard.append(accept_btn)
            inline_keyboard.append(decline_btn)
        elif data == 'accept_exit':
            current_room = member.last_room
            relation = RoomMember.objects.get(room = current_room, member = member)
            relation.delete()
            answer = 'Вы успешно покинули комнату.'
        elif data == "decline_exit":
            current_room = member.last_room
            answer = f"Выбрана комната *{current_room.name}* с идентификатором\n`{current_room.id}`\n Что вы хотите сделать?"
            member.last_room = current_room
            member.save()
            room_member = RoomMember.objects.get(room=current_room, member=member)
            if room_member.is_admin:
                if not current_room.is_started:
                    start_room_btn = [{'text': 'Начать игру', 'callback_data': 'start_room'}]
                else:
                    start_room_btn = []
                edit_room_name_btn = [{'text': 'Изменить название', 'callback_data': 'edit_room_name'}]
                edit_room_description_btn = [{'text': 'Изменить описание', 'callback_data': 'edit_room_description'}]
                delete_room_btn = [{'text': 'Удалить', 'callback_data': 'delete_room'}]
                inline_keyboard = [start_room_btn, edit_room_name_btn, edit_room_description_btn, delete_room_btn]
            if not current_room.is_started:
                exit_room_btn = [{'text': 'Покинтуть комнату', 'callback_data': 'exit_room'}]
                inline_keyboard.append(exit_room_btn)
            edit_wish_btn = [{'text': 'Изменить пожелание', 'callback_data': 'edit_wish'}]
            watch_receiver_btn = [{'text': 'Инфо о получателе', 'callback_data': 'watch_receiver'}]
            inline_keyboard.append(edit_wish_btn)
            inline_keyboard.append(watch_receiver_btn)
        elif data == 'delete_room':
            current_room = member.last_room
            try:
                room_member = RoomMember.objects.get(room=current_room, member=member, is_admin=True)
                answer = f"Вы уверены, что хотите удалить игру? Это действие не отменить."
                accept_btn = [{'text': 'Да', 'callback_data': 'accept_delete'}]
                decline_btn = [{'text': 'Отмена', 'callback_data': 'decline_delete'}]
                inline_keyboard.append(accept_btn)
                inline_keyboard.append(decline_btn)
            except ObjectDoesNotExist:
                answer = 'Вы не являетесь админом этой комнаты!'
        elif data == "accept_delete":
            try:
                current_room = member.last_room
                room_name, room_id = current_room.name, current_room.id
                recipients = list(Member.objects.filter(roommember__room=current_room, roommember__is_admin=False).values_list('chat_id', flat=True))
            except ObjectDoesNotExist:
                answer = 'Произошла ошибка. Комната не найдена'
                edit_message.delay(answer, chat.id, message["message_id"], [])
                return JsonResponse({"ok": "POST request processed"})
            try:
                current_room.delete()
                answer = f'Комната *{room_name}* с идентификатором `{room_id}` удалена! Всем участникам придет сообщение об удалении.'
                edit_message.delay(answer, chat.id, message["message_id"], [])
                answer = f'Комната *{room_name}* с идентификатором `{room_id}` удалена!'
                mailing.delay(answer, recipients)
                return JsonResponse({"ok": "POST request processed"})
            except:
                answer = 'Произошла ошибка. Комната не была удалена'
                send_message.delay(answer, chat.id)
                return JsonResponse({"ok": "POST request processed"})
        elif data == "decline_delete":
            current_room = member.last_room
            answer = f"Выбрана комната *{current_room.name}* с идентификатором\n`{current_room.id}`\n Что вы хотите сделать?"
            member.last_room = current_room
            member.save()
            room_member = RoomMember.objects.get(room=current_room, member=member)
            if room_member.is_admin:
                if not current_room.is_started:
                    start_room_btn = [{'text': 'Начать игру', 'callback_data': 'start_room'}]
                else:
                    start_room_btn = []
                edit_room_name_btn = [{'text': 'Изменить название', 'callback_data': 'edit_room_name'}]
                edit_room_description_btn = [{'text': 'Изменить описание', 'callback_data': 'edit_room_description'}]
                delete_room_btn = [{'text': 'Удалить', 'callback_data': 'delete_room'}]
                inline_keyboard = [start_room_btn, edit_room_name_btn, edit_room_description_btn, delete_room_btn]
            if not current_room.is_started:
                exit_room_btn = [{'text': 'Покинтуть комнату', 'callback_data': 'exit_room'}]
                inline_keyboard.append(exit_room_btn)
            edit_wish_btn = [{'text': 'Изменить пожелание', 'callback_data': 'edit_wish'}]
            watch_receiver_btn = [{'text': 'Инфо о получателе', 'callback_data': 'watch_receiver'}]
            inline_keyboard.append(edit_wish_btn)
            inline_keyboard.append(watch_receiver_btn)
        elif data == 'edit_wish':
            member.state = 6
            member.save()
            answer = "Опишите свое желание, можно оставлять ссылки."
        elif data == 'watch_receiver':
            current_room = member.last_room
            try:
                room_member = RoomMember.objects.get(room=current_room, member=member)
                receiver = room_member.receiver
                room_receiver = RoomMember.objects.get(room=current_room, member=receiver)
                answer = f'Вы дарите подарок :\n{receiver.first_name}  {receiver.last_name}\nПожелание:\n`{room_receiver.wish}`'
            except ObjectDoesNotExist:
                answer = "Что-то пошло не так. Попробуйте еще раз."
        else:
            answer = "Что-то пошло не так. Попробуйте еще раз."
    else:
        answer = "Что-то пошло не так. Попробуйте еще раз."
    reply_markup = json.dumps({"inline_keyboard":inline_keyboard})
    edit_message.delay(answer, chat.id, message["message_id"], reply_markup)
    return JsonResponse({"ok": "POST request processed"})







