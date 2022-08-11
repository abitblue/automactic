echo "===Installing Chromium Browser==="
sudo apt install chromium-browser
echo "===Installing Kiosk Service==="
sudo cp kiosk.sh /etc/systemd/user
sudo cp kiosk.service /etc/systemd/user
sudo chmod +x /etc/systemd/user/kiosk.sh
echo "===Enabling Kiosk Service==="
systemctl --user enable kiosk.service
systemctl --user start kiosk.service
echo "===Installation Complete==="