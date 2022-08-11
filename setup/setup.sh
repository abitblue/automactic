echo "Installing Chromium Browser\n"
sudo apt install chromium-browser
echo "Installing Kiosk Service\n"
sudo cp kiosk.sh /etc/systemd/user
sudo cp kiosk.service /etc/systemd/user
echo "Enabling Kiosk Service\n"
systemctl --user enable kiosk.service
systemctl --user start kiosk.service
echo "Installation Complete\n"