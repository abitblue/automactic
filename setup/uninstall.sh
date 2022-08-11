echo "===Uninstalling Chromium Browser==="
sudo apt remove chromium-browser
echo "===Disabling Kiosk Service==="
systemctl --user disable kiosk.service
systemctl --user stop kiosk.service
echo "===Uninstalling Kiosk Service==="
sudo rm /etc/systemd/user/kiosk.sh 
sudo rm /etc/systemd/user/kiosk.service
echo "===Uninstallation Complete==="