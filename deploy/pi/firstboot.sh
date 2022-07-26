#!/usr/bin/env bash

# Enable output
set -x

# Pull in env vars
# shellcheck disable=SC2046
export $(grep -v '^#' /boot/firstboot/config.env | xargs -d '\n')


# Hostname
hostnamectl set-hostname "${HOSTNAME}"
# shellcheck disable=SC2002
CURRENT_HOSTNAME=$(cat /etc/hostname | tr -d " \t\n\r")
sed -i "s/127.0.1.1.*${CURRENT_HOSTNAME}/127.0.1.1\t${HOSTNAME}/g" /etc/hosts

# User Password
USERNAME=$(getent passwd 1000 | cut -d: -f1)
echo "${USERNAME}:${USER_PASSWD}" | chpasswd

# Locale + Keyboard + Time
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
sed -i "s/^\s*LANG=\S*/LANG=en_US.UTF-8/" /etc/default/locale
cat > /etc/default/keyboard <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="us"
XKBVARIANT=""
XKBOPTIONS=""

BACKSPACE="guess"
EOF
dpkg-reconfigure -f noninteractive locales
dpkg-reconfigure -f noninteractive keyboard-configuration
dpkg-reconfigure -f noninteractive tzdata
timedatectl set-timezone "${TIMEZONE}"
timedatectl set-ntp true

# Enable ssh, disable root login
systemctl enable --now ssh
sed -i 's/#\?\(PermitRootLogin\s*\).*$/\1 no/' /etc/ssh/sshd_config

# Enable IP Forwarding
cat > /etc/sysctl.d/30-ipforward.conf <<EOF
net.ipv4.ip_forward=1
net.ipv6.conf.default.forwarding=1
net.ipv6.conf.all.forwarding=1
EOF

# Set CRDA region to US
sed -i -E 's/^(REGDOMAIN[[:blank:]]*=[[:blank:]]*).*/\1us/' /etc/default/crda

# Unblock the Pi's wlan interface (Wifi Dongle)
rfkill unblock wlan

# dhcpcd Configuration
if [ ! -f  /etc/dhcpcd.conf.bak ]; then
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak
fi
cat << EOF >> /etc/dhcpcd.conf
##################################
denyinterfaces wlan0 vx-eth0.${VXLAN_ID}
interface eth0
    static domain_name_servers=1.1.1.1 8.8.8.8 1.0.0.1 8.8.4.4
EOF

# update apt cache, ingore "Release file... is not valid yet." error
apt update -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false
if [ -z ${APT_UPGRADE_SKIP+x} ]; then apt upgrade -y; else echo "APT_SKIP DEFINED, SKIPPING UPGRADES"; fi

# Install software
apt install -y dnsutils hostapd vim tmux dos2unix nftables

# Setup nftables
# TODO: setup nftables

# Setup hostpad
export LAN_CHANNEL=${LAN_CHANNEL:-"acs_survey"}
envsubst < /boot/firstboot/hostapd.conf > /etc/hostapd/hostapd.conf
systemctl unmask hostapd

# Setup vxlan
systemctl enable systemd-networkd


# Log and finalize
journalctl -u firstboot.service > /home/pi/firstboot.log
systemd-run --no-block sh -c "sleep 15 && systemctl reboot"