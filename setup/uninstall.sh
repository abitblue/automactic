echo "===Uninstalling Chromium Browser==="
sudo apt remove chromium-browser
echo "===Disabling Kiosk Service==="
systemctl --user disable kiosk.service
systemctl --user stop kiosk.service
systemctl --user disable kioskdjango.service
systemctl --user stop kioskdjango.service
echo "===Uninstalling Kiosk Service==="
sudo rm /etc/systemd/user/kiosk.sh 
sudo rm /etc/systemd/user/kiosk.service
sudo rm /etc/systemd/user/kioskdjango.service
echo "===Uninstallation Complete==="