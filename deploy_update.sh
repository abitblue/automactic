#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

cd "${BASEDIR}"
source "${BASEDIR}/venv/bin/activate"
git pull
pip install -r /opt/automactic/requirements.txt
set -o allexport; source /opt/automactic/.env; set +o allexport
python manage.py collectstatic --no-input
systemctl restart automactic-wsgi nginx
