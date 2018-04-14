from config import settings
from common.email.mail_agent import mail_agent

# 记录上一次邮件发送的时间
last_mail_datetime = None

def send_mail(title, content):
    if not mail_agent:
        return
    global last_mail_datetime
    now = datetime.datetime.now()
    if last_mail_datetime and now - last_mail_datetime < datetime.timedelta(
            minutes=settings.N_MINUTES_STATE):
        return
    last_mail_datetime = now
    with mail_agent.SMTP() as s:
        s.send(settings.MAIL_RECEIPIENTS, content, title)