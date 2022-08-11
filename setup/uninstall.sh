sudo apt remove chromium-browser
cd /etc/systemd/user
sudo systemctl --user disable kiosk.service
sudo systemctl --user stop kiosk.service
sudo rm /etc/systemd/user/kiosk.sh 
sudo rm /etc/systemd/user/kiosk.service