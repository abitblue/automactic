sudo apt remove chromium-browser
sudo systemctl --user disable kiosk.service
sudo systemctl --user stop kiosk.service
sudo rm /etc/systemd/user/kiosk.sh 
sudo rm /etc/systemd/user/kiosk.service