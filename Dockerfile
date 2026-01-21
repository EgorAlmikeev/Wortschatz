# stage 1: development with tests
FROM python:3.12-slim AS dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

# stage 2: production (no tests)
FROM python:3.12-slim AS prod

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY manage.py /app/manage.py
COPY requirements.txt /app/requirements.txt
COPY entrypoint.sh /app/entrypoint.sh
COPY wortschatz /app/wortschatz
COPY my_jwt_auth /app/my_jwt_auth
COPY word_collection /app/word_collection

RUN pip install --upgrade pip && pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
