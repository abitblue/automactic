## dnsmasq clobbers the local resolver, disable it from listening on loopback iface
#echo "DNSMASQ_EXCEPT=lo" >> /etc/default/dnsmasq
#

# git
# nftables
# dnsmasq
  # dnsmasq clobbers the local resolver, disable it from listening on loopback iface
  echo "DNSMASQ_EXCEPT=lo" >> /etc/default/dnsmasq

# postgres
# vxlan

# nginx
server_names_hash_bucket_size 64;

server {
    access_log  off;
    listen      80 default_server;
    listen      [::]:80 default_server;
    server_name  _;

    return 302 http://wifi.siths.org;
}

server {
    listen      80;
    listen      [::]:80;
    server_name wifi.siths.org www.wifi.siths.org automactic-110-1.local www.automactic-110-1.local;

    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;

    location = /favicon.ico { access_log off; log_not_found off; }

    location ~* (?=/static/).*\.svgz {
        root /opt/automactic/;
        access_log off;

        # prevent gzipping of already gzipped resource
        gzip off;
        add_header Content-Encoding "gzip";
    }


    location /static/ {
        root /opt/automactic/;
        access_log off;
    }


    location / {
        include        proxy_params;
        proxy_pass     http://unix:/tmp/automactic-wsgi.socket;
    }
}

# python poetry
# gunicorn
