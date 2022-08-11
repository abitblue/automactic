sudo apt remove chromium-browser
systemctl --user disable kiosk.service
systemctl --user stop kiosk.service
rm /etc/systemd/user/kiosk.sh 
rm /etc/systemd/user/kiosk.service