sudo apt install chromium-browser
sudo cp kiosk.sh /etc/systemd/user
sudo cp kiosk.service /etc/systemd/user
sudo systemctl --user enable kiosk.service
sudo systemctl --user start kiosk.service