import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secretsanta.settings')

app = Celery('tg_bot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_queues = [
    Queue('messages'),
    Queue('messages_tokens', max_length=1)
]
app.autodiscover_tasks()


@app.task
def token():
    return 1

# настраиваем постоянный выпуск нашего токена
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # мы будем выпускать по 30 токену в секунду
    sender.add_periodic_task(5, token.signature(queue='messages_tokens'))