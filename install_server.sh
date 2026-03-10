#!/bin/sh
# Installs the stats web server and enables it at boot.
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing stats server..."
mkdir -p /opt/statsserver
cp "$REPO_DIR/server/server.py" /opt/statsserver/
cp "$REPO_DIR/server/S99statsserver" /etc/init.d/
chmod +x /etc/init.d/S99statsserver

echo "Starting stats server..."
/etc/init.d/S99statsserver restart 2>/dev/null || /etc/init.d/S99statsserver start

IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
echo ""
echo "Done! Stats server running at http://${IP:-<device-ip>}:8080"
