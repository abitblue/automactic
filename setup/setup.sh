sudo apt install chromium-browser
sudo cp kiosk.sh /etc/systemd/user
sudo cp kiosk.service /etc/systemd/user
cd /etc/systemd/user && sudo systemctl --user enable kiosk.service
cd /etc/systemd/user && sudo systemctl --user start kiosk.service