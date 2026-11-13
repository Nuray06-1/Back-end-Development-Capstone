#!/bin/sh
set -eu
python manage.py migrate --noinput
# Create an administrator interactively when needed; no shared default password.
exec "$@"
