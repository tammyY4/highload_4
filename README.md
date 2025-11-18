Видео : как работает имеет название "без звука"
В ходе работы у меня возникла ошибка : я попыталась ее объяснить в видео "со звуком", так как не могу понять в чем загвоздка

1. Установка Python и pip
python --version
pip --version

2. Установка зависимостей
pip install fastapi celery redis aiosmtplib pydantic uvicorn

4. Запуск Redis сервера
docker run -p 6379:6379 redis:latest

5. Запуск Celery
В дериктории проекта
celery -A celery_worker.celery_app worker --loglevel=info

6. Запуск FastAPI
В новой вкладке терминала запустите:
uvicorn main:app --reload

7. Проверка работы
http://localhost:8000/docs
