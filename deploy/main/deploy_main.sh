# config.env
# VX_VNI
# VX_GROUP
# IP_PREFIX

# Required Prereqs:
# - git
# - nftables
# - dnsmasq
# - postgresql postgresql-contrib libpq-dev
# - nginx
# - python3-wheel
# - python3-distutils
# - avahi-daemon
# - build-essential wget curl xz-utils libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
# - poetry
# - pyenv, 3.10.5

# Postgres Setup
# $ sudo -u postgres psql
# CREATE DATABASE automactic;
# CREATE USER amacadmin WITH PASSWORD 'passwod';
# ALTER ROLE amacadmin SET client_encoding TO 'utf8';
# ALTER ROLE amacadmin SET default_transaction_isolation TO 'read committed';
# ALTER ROLE amacadmin SET timezone TO 'UTC';
# GRANT ALL PRIVILEGES ON DATABASE automactic TO amacadmin;
# $ pg_ctlcluster 13 main start

# pgadmin setup
./pgadmin4.sh


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sudo apt install sudo git nftables dnsmasq postgresql nginx build-essential avahi-daemon python3-poetry

# systemd-networkd setup
for i in "${SCRIPT_DIR}"/*.{link,netdev,network}; do
    [ -f "$i" ] || break  # Guard against nonexistant files
    envsubst < "$i" > "/etc/systemd/network/$(basename "$i")"
done
systemctl enable systemd-networkd


# dnsmasq setup, dnsmasq clobbers the local resolver, disable it from listening on loopback iface
echo "DNSMASQ_EXCEPT=lo" >> /etc/default/dnsmasq
envsubst < "${SCRIPT_DIR}/dnsmasq.conf" >> /etc/dnsmasq.conf
systemctl enable dnsmasq

# TODO: nftables

# TODO: nginx + web stack
sudo cp pgadmin4.service /etc/system