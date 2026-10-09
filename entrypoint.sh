#!/bin/sh

set -e

echo "--> Exécution des migrations..."
python manage.py migrate --noinput

echo "--> Creation des groups..."
python manage.py loaddata app/permissions/initial_group.json 

echo "--> Creation des permissions..."
python manage.py add_permissions

echo "--> Creation de l'administrateur..."
# Retrait de --noinput ici
python manage.py create_admin

echo "--> Suppression des permissions inutiles..."
# Retrait de --noinput ici
python manage.py delete_permissions

echo "--> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "--> Démarrage de Uvicorn..."
exec "$@"