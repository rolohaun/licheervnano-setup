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

# ── Git (via Python3 HTTP clone) ─────────────────────────────────────────────

echo "[3/3] Installing git-over-python helper (mgit)..."
cat > /usr/bin/mgit << 'PYEOF'
#!/usr/bin/env python3
"""Minimal clone/pull using GitHub tarball API. Usage: mgit clone <url> [dir]"""
import sys, os, tarfile, urllib.request, io

def gh_api_url(url):
    url = url.rstrip("/").removesuffix(".git")
    parts = url.split("/")
    owner, repo = parts[-2], parts[-1]
    return f"https://api.github.com/repos/{owner}/{repo}/tarball/master", repo

def download_and_extract(api_url, dest):
    os.makedirs(dest, exist_ok=True)
    req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
    print("Downloading...", flush=True)
    with urllib.request.urlopen(req) as r:
        data = io.BytesIO(r.read())
    print("Extracting...", flush=True)
    prefix = None
    with tarfile.open(fileobj=data, mode="r:gz") as tf:
        for m in tf.getmembers():
            if prefix is None:
                prefix = m.name.split("/")[0] + "/"
            m.name = m.name[len(prefix):]
            if m.name:
                tf.extract(m, dest)
    print("Done.")

def clone(url, dest=None):
    api_url, repo = gh_api_url(url)
    dest = dest or repo
    if os.path.exists(dest):
        print(f"mgit: '{dest}' already exists"); sys.exit(1)
    print(f"Cloning {url} -> {dest} ...")
    download_and_extract(api_url, dest)

def pull(url):
    api_url, _ = gh_api_url(url)
    print(f"Pulling latest ...")
    download_and_extract(api_url, ".")

if len(sys.argv) < 3:
    print("Usage: mgit clone <github-url> [dir]\n       mgit pull  <github-url>"); sys.exit(1)
cmd = sys.argv[1]
if cmd == "clone":
    clone(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
elif cmd == "pull":
    pull(sys.argv[2])
else:
    print(f"mgit: unknown command"); sys.exit(1)
PYEOF
chmod +x /usr/bin/mgit
echo "mgit installed. Use: mgit clone https://github.com/owner/repo"

echo ""
echo "Setup complete!"
