#!/bin/sh
echo "Applying database migrations..."
python manage.py migrate
echo "Database migrations successfully applied."

echo "Starting server..."
exec "$@"
echo "Server successfully started."