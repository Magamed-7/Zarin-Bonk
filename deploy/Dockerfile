FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Статика собирается на сборке образа, чтобы контейнер стартовал сразу и не зависел от
# прав на запись в рабочий каталог. Ключ на этом шаге не важен — collectstatic ничего
# не подписывает, но без переменной Django не импортируется.
RUN SECRET_KEY=build-only DEBUG=False python manage.py collectstatic --noinput

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--timeout", "60", "--access-logfile", "-"]
