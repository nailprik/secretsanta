from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from secretsanta.settings import TELEGRAM_BOT_TOKEN
from tgbot.utils import set_webhook
from tgbot.views import TelegramBotView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'bot{TELEGRAM_BOT_TOKEN}/', csrf_exempt(TelegramBotView.as_view()))
]

set_webhook()
