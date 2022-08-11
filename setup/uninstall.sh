sudo apt remove chromium-browser
systemctl --user disable kiosk.service
systemctl --user stop kiosk.service
sudo rm /etc/systemd/user/kiosk.sh 
sudo rm /etc/systemd/user/kiosk.service