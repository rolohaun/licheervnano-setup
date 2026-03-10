# LicheeRV Nano Buildroot Setup

Automates WiFi, git, and a device stats web server on a fresh [LicheeRV Nano](https://wiki.sipeed.com/hardware/en/lichee/RV_Nano/1_intro.html) Buildroot install.

## What it does

1. Writes `/etc/wpa_supplicant.conf` with your WiFi credentials
2. Starts WiFi via `/etc/init.d/S30wifi` and waits for an IP
3. Downloads and installs `git 2.53.0` from Alpine Linux (musl-compatible, riscv64)

## Usage

Connect to the device over USB (SSH to `10.19.172.1` as `root`/`root`), then:

```sh
# Download and run the setup script
curl -sL https://raw.githubusercontent.com/rolohaun/licheervnano-setup/master/setup.sh -o setup.sh
sh setup.sh "YourSSID" "YourPassword"

# Then clone this repo and install the stats server
mgit clone https://github.com/rolohaun/licheervnano-setup
cd licheervnano-setup
sh install_server.sh
```

> **Note:** `mgit` is a lightweight Python3-based clone/pull tool installed by `setup.sh`.
> It uses the GitHub tarball API so no git binary is needed for cloning.
> Use `mgit pull` inside a cloned directory to update it.

## Stats Web Server

A lightweight Python3 HTTP server that displays live device stats at `http://<device-ip>:8080`.

**Shows:**
- Hostname, kernel version, architecture
- Uptime
- CPU usage % + load average + temperature
- Memory usage (used / free / total)
- Disk usage ( / )

Auto-refreshes every 3 seconds.

### Manual install

```sh
mkdir -p /opt/statsserver
cp server/server.py /opt/statsserver/
cp server/S99statsserver /etc/init.d/
chmod +x /etc/init.d/S99statsserver
/etc/init.d/S99statsserver start
```

## Notes

- The rootfs is a persistent ext4 partition — all changes survive reboots
- WiFi connects automatically on every boot via `/etc/init.d/S30wifi`
- Stats server starts automatically on boot via `/etc/init.d/S99statsserver`
- Tested on Buildroot image with kernel `5.10.4` (January 2026 build)
