#!/bin/sh
echo "Applying database migrations..."
until python manage.py migrate --noinput; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 3
done
echo "Database migrations successfully applied."

echo "Starting server..."
exec "$@"
echo "Server successfully started."