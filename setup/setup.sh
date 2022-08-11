sudo apt install chromium-browser
sudo cp kiosk.sh /etc/systemd/user
sudo cp kiosk.service /etc/systemd/user
systemctl --user enable kiosk.service
systemctl --user start kiosk.service