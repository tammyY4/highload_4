from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
import uuid
import redis
from datetime import datetime
from config import REDIS_URL, TOKEN_EXPIRY_MINUTES, MESSAGE_TTL
from celery_worker import send_email

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
app = FastAPI()

class RegistrationRequest(BaseModel):
  email: EmailStr
class ForgotRequest(BaseModel):
    email: EmailStr
class SetPasswordRequest(BaseModel):
  token: str
  password: str
class ChatMessage(BaseModel):
  user: str
  message: str

from celery_worker import send_email, simple_task

send_email.delay('yutoma@yandex.ru', 'Subject', 'Content')
simple_task.delay('one', 'two', 'three')

# РЕГИСРАЦИЯ
@app.post("/register")
async def register_user(req: RegistrationRequest):
  token = str(uuid.uuid4())
  redis_client.setex(f"register_token:{token}", TOKEN_EXPIRY_MINUTES, req.email)
  link = f"http://localhost:8000/set-password?token={token}"
  send_email.delay(req.email, "Регистрация", f"Нажмите на ссылку для установки пароля: {link}")
  return {"msg": "Письмо отправлено на почту"}


# ОТПРАВКА СООБЩЕНИЙ
@app.post("/chat/send")
async def chat_send(msg: ChatMessage):
  msg_id = str(uuid.uuid4())
  redis_client.hmset(f"chat_msg:{msg_id}", {
    "user": msg.user,
    "message": msg.message,
    "timestamp": datetime.utcnow().isoformat()
  })
  redis_client.expire(f"chat_msg:{msg_id}", MESSAGE_TTL)
  redis_client.lpush("chat_history", msg_id)
  redis_client.expire("chat_history", MESSAGE_TTL)
  return {"msg": "Сообщение отправлено"}


# ИСТОРИЯ СООБЩЕНИЯ
@app.get("/chat/history")
async def chat_history():
  msg_ids = redis_client.lrange("chat_history", 0, -1)
  messages = []
  for msg_id in msg_ids:
    message = redis_client.hgetall(f"chat_msg:{msg_id}")
    if message:
      messages.append(message)
  return messages


# ПАРОЛЬ
@app.post("/set-password")
async def set_password(req: SetPasswordRequest):
    email = redis_client.get(f"register_token:{req.token}")
    if not email:
        raise HTTPException(status_code=410, detail="Токен невалидный")
    # Здесь добавить логику сохранения пароля для email
    redis_client.delete(f"register_token:{req.token}")
    return {"msg": "Пароль установлен, регистрация завершена"}

# ЗАБЫЛ
@app.post("/forgot-password")
async def forgot_password(req: ForgotRequest):
  token = str(uuid.uuid4())
  redis_client.setex(f"reset_token:{token}", TOKEN_EXPIRY_MINUTES, req.email)
  link = f"http://localhost:8000/reset-password?token={token}"
  send_email.delay(req.email, "Восстановление пароля", f"Восстановить пароль: {link}")
  return {"msg": "Письмо отправлено на почту"}


# СБРОС
@app.post("/reset-password")
async def reset_password(req: SetPasswordRequest):
  email = redis_client.get(f"reset_token:{req.token}")
  if not email:
    raise HTTPException(status_code=410, detail="Токен невалидный")
  redis_client.delete(f"reset_token:{req.token}")
  return {"msg": "Пароль был изменён"}
