#!/bin/sh
echo "Waiting for PostgreSQL..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "Applying database migrations..."
python manage.py migrate
echo "Database migrations successfully applied."

echo "Starting server..."
exec "$@"
echo "Server successfully started."