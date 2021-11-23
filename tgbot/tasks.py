import requests

from secretsanta.celery import app
from secretsanta.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN


def rate_limit(task, task_group):
    # берем соединение с брокером из пула
    with task.app.connection_for_read() as conn:
        # забираем токен
        msg = conn.default_channel.basic_get(task_group+'_tokens', no_ack=True)
        # получили None - очередь пуста, токенов нет
        if msg is None:
            # повторить таску через 1 сек
            task.retry(countdown=1)


@app.task(bind=True, queue='messages', max_retries=None)
def send_message(self, text, chat_id, reply_markup=None):
    rate_limit(self, 'messages')
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup,
        "parse_mode": "Markdown"
    }
    response = requests.post(f"{TELEGRAM_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data=data)
    print(response.content)


@app.task(bind=True, queue='messages', max_retries=None)
def edit_message(self, text, chat_id, message_id, reply_markup=None):
    rate_limit(self, 'messages')
    data = {
        "chat_id": chat_id,
        "text": text,
        "message_id": message_id,
        "reply_markup": reply_markup,
        "parse_mode": "Markdown"
    }
    response = requests.post(f"{TELEGRAM_URL}/bot{TELEGRAM_BOT_TOKEN}/editMessageText", data=data)
    print(response.content)


@app.task(bind=True, queue='messages', max_retries=None)
def mailing(self, answer, recipients):
    for recipient in recipients:
        send_message.delay(answer, recipient)
    print(f"Рассылка произведена по {len(recipients)} чатам")