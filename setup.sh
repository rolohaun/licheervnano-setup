#!/bin/sh
# LicheeRV Nano Buildroot Setup Script
# Configures WiFi and installs git on a fresh Buildroot install.
# Usage: ./setup.sh <ssid> <password>

set -e

SSID="$1"
PASS="$2"

if [ -z "$SSID" ] || [ -z "$PASS" ]; then
    echo "Usage: $0 <ssid> <password>"
    exit 1
fi

# ── WiFi ─────────────────────────────────────────────────────────────────────

echo "[1/3] Writing WiFi config..."
cat > /etc/wpa_supplicant.conf << EOF
ctrl_interface=/var/run/wpa_supplicant
ap_scan=1
network={
  ssid="$SSID"
  psk="$PASS"
}
EOF

echo "[2/3] Starting WiFi..."
killall wpa_supplicant udhcpc 2>/dev/null || true
rm -f /var/run/wpa_supplicant/wlan0
sleep 1
/etc/init.d/S30wifi start

# Wait up to 20 seconds for an IP address
echo "Waiting for IP address..."
i=0
while [ $i -lt 20 ]; do
    IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
    if [ -n "$IP" ]; then
        echo "Connected! IP: $IP"
        break
    fi
    sleep 1
    i=$((i + 1))
done

if [ -z "$IP" ]; then
    echo "ERROR: Failed to get IP address. Check SSID/password and try again."
    exit 1
fi

# ── Git ───────────────────────────────────────────────────────────────────────

echo "[3/3] Installing git..."
cd /tmp
curl -sL 'https://dl-cdn.alpinelinux.org/alpine/edge/main/riscv64/git-2.53.0-r0.apk' -o git.apk
mkdir -p /tmp/git_extract
gzip -d < git.apk | tar x -C /tmp/git_extract 2>/dev/null || true
cp /tmp/git_extract/usr/bin/git* /usr/bin/
cp -r /tmp/git_extract/usr/lib/git-core /usr/lib/
cp -r /tmp/git_extract/usr/share/git-core /usr/share/ 2>/dev/null || true
rm -rf /tmp/git.apk /tmp/git_extract

git --version && echo "git installed successfully."

echo ""
echo "Setup complete!"
