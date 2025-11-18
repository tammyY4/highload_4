from celery import Celery
from aiosmtplib import SMTP
from email.message import EmailMessage
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL


celery_app = Celery('email_tasks', broker='redis://localhost/0')

@celery_app.task
def simple_task(a, b, c):
  print(a, b, c)

# Вызов:
simple_task.delay('one', 'two', 'three')