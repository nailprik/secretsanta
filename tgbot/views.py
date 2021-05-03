import json

from django.http import JsonResponse
from django.views import View

from tgbot.models import Chat, Member
from tgbot.utils import send_message, message_handler, callback_handler


class TelegramBotView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        message = data.get('message')
        if message:
            return message_handler(message)
        callback_query = data.get('callback_query')
        if callback_query:
            return callback_handler(callback_query)



