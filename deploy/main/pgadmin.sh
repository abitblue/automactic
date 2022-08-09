sudo curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'
sudo apt install pgadmin4

sudo adduser --system --home /var/lib/pgadmin --disabled-login --shell /usr/sbin/nologin pgadmin4
sudo mkdir /var/log/pgadmin
sudo chown pgadmin4 /var/log/pgadmin

cat << EOF | sudo tee /etc/pgadmin/config_system.py
LOG_FILE = '/var/log/pgadmin/pgadmin4.log'
SQLITE_PATH = '/var/lib/pgadmin/pgadmin4.db'
SESSION_DB_PATH = '/var/lib/pgadmin/sessions'
STORAGE_DIR = '/var/lib/pgadmin/storage'
EOF

sudo -u pgadmin4 /bin/bash -c "cd /usr/pgadmin4 && source venv/bin/activate && cd web && python setup.py"
sudo chown pgadmin4:nogroup -R /var/lib/pgadmin

sudo cp pgadmin4.service