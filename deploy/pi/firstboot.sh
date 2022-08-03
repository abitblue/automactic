#!/usr/bin/env bash

# Enable output
set -x

# Req Vars:
# HOSTNAME
# TIMEZONE
# USER_PASSWD
# VX_VNI
# VX_GROUP
# SSID
# WIFI_CHANNEL

# Optional:
# APT_UPGRADE_SKIP: If defined, will skip apt upgrade

# Pull in env vars
# shellcheck disable=SC2046
export $(grep -v '^#' /boot/firstboot/config.env | xargs -d '\n')


# Hostname
hostnamectl set-hostname "${HOSTNAME}"
sed -i "s/raspberrypi/${HOSTNAME}/g" /etc/hosts

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

# update apt cache and install software, ingore "Release file... is not valid yet." error
apt update -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false
if [ -z ${APT_UPGRADE_SKIP+y} ]; then apt upgrade -y; else echo "APT_SKIP DEFINED, SKIPPING UPGRADES"; fi
apt install -y hostapd vim tmux dos2unix nftables tcpdump

# Enable ssh, disable root login
systemctl enable ssh
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

# Network configuration - Use systemd netorking
# Remove non-systemd networking packages
apt remove --purge --auto-remove dhcpcd5 fake-hwclock ifupdown isc-dhcp-client isc-dhcp-common openresolv

# Install conf files
for i in /boot/firstboot/*.{link,netdev,network}; do
    [ -f "$i" ] || break  # Guard against nonexistant files
    envsubst < "$i" > "/etc/systemd/network/$(basename "$i")"
done

# Disable wpa_supplicant for ap0 via dhcpcd
cat << EOF >> /etc/dhcpcd.conf
################################
noarp
interface ap0
    nobook wpa_supplicant
EOF

# Install hostapd configurations
cp /boot/firstboot/hostapd@.service /etc/systemd/system
mkdir -p /etc/hostapd
envsubst < /boot/firstboot/hostapd.conf > /etc/hostapd/ap0.conf

# Enable systemd network services
systemctl daemon-reload
systecmtl enable hostapd@ap0
systemctl disable wpa_supplicant
systemctl enable systemd-networkd
ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

# Setup nftables
# TODO: setup nftables

# Setup automated reboot every day
systemctl daemon-reload
cp /boot/firstboot/sched-reboot.service /etc/systemd/system
cp /boot/firstboot/sched-reboot.timer /etc/systemd/system
systemctl enable sched-reboot.timer

# Log and finalize
journalctl -u firstboot.service > /boot/firstboot.log

# Enable overlayfs
raspi-config nonint enable_overlayfs

systemd-run --no-block sh -c "sleep 15 && systemctl reboot"
