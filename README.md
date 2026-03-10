# LicheeRV Nano Buildroot Setup

Automates WiFi and git setup on a fresh [LicheeRV Nano](https://wiki.sipeed.com/hardware/en/lichee/RV_Nano/1_intro.html) Buildroot install.

## What it does

1. Writes `/etc/wpa_supplicant.conf` with your WiFi credentials
2. Starts WiFi via `/etc/init.d/S30wifi` and waits for an IP
3. Downloads and installs `git 2.53.0` from Alpine Linux (musl-compatible, riscv64)

## Usage

Connect to the device over USB (SSH to `10.19.172.1` as `root`/`root`), then:

```sh
# Download the script
curl -sL https://raw.githubusercontent.com/rolohaun/licheervnano-setup/main/setup.sh -o setup.sh

# Run it with your WiFi credentials
sh setup.sh "YourSSID" "YourPassword"
```

## Notes

- The rootfs is a persistent ext4 partition — all changes survive reboots
- WiFi connects automatically on every boot via `/etc/init.d/S30wifi`
- Tested on Buildroot image with kernel `5.10.4` (January 2026 build)
