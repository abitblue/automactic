sudo apt install chromium-browser
cp kiosk.sh /etc/systemd/user
cp kiosk.service /etc/systemd/user
systemctl --user enable kiosk.service
systemctl --user start kiosk.service