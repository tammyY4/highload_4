from celery import Celery
from aiosmtplib import SMTP
from email.message import EmailMessage
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL


celery_app = Celery('email_tasks', broker='redis://localhost/0')

@celery_app.task(name='send_email')
def send_email(to_email, subject, content):
  print('ARGS:', to_email, subject, content)
  msg = EmailMessage()
  msg["From"] = DEFAULT_FROM_EMAIL
  msg["To"] = to_email
  msg["Subject"] = subject
  msg.set_content(content)

  smtp = SMTP(hostname=EMAIL_HOST, port=EMAIL_PORT, username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
  smtp.connect()
  smtp.send_message(msg)
  smtp.quit()

@celery_app.task
def simple_task(a, b, c):
  print(a, b, c)