echo "===Installing Chromium Browser==="
sudo apt install chromium-browser
echo "===Installing Kiosk Service==="
sudo cp kiosk.sh /etc/systemd/user
sudo cp kiosk.service /etc/systemd/user
sudo chmod +x /etc/systemd/user/kiosk.sh
sudo cp kioskdjango.service /etc/systemd/user
echo "===Enabling Kiosk Service==="
systemctl --user enable kiosk.service
systemctl --user start kiosk.service
systemctl --user enable kioskdjango.service
systemctl --user start kioskdjango.service
systemctl --user daemon-reload
systemctl --user daemon-reload
systemctl --user restart kiosk.service
systemctl --user restart kioskdjango.service
echo "===Installation Complete==="