# =====================
# Base stage
# =====================
FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["./entrypoint.sh"]


# =====================
# Dev stage
# =====================
FROM base AS dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# =====================
# Prod stage
# =====================
FROM base AS prod
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
