FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "wortschatz.wsgi:application", "--bind", "0.0.0.0:8000"]
