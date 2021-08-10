#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

cd "${BASEDIR}"
source "${BASEDIR}/venv/bin/activate" &&
git pull &&
pip install -r /opt/automactic/requirements.txt &&
set -o allexport; source /opt/automactic/.env; set +o allexport &&
python manage.py collectstatic --no-input &&
systemctl restart automactic-wsgi nginx &&
curl "http://10.94.164.118/ping_deploy_success?fromip=$(ifconfig eth0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')&fromhostname=${HOSTNAME}" \
  -H 'User-Agent: automactic-ping/0.0.1' \
  --insecure