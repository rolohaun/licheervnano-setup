#!/bin/sh
# Sets up a swap file to extend available memory.
# The LicheeRV Nano has only 128MB usable RAM (128MB is reserved for camera/display).
# Usage: sh install_swap.sh [size]   e.g. sh install_swap.sh 512M (default: 512M)
set -e

SIZE="${1:-512M}"
SWAPFILE="/swapfile"

if grep -q "$SWAPFILE" /proc/swaps 2>/dev/null; then
    echo "Swap already active on $SWAPFILE"
    free -m
    exit 0
fi

echo "Creating ${SIZE} swap file at ${SWAPFILE}..."
fallocate -l "$SIZE" "$SWAPFILE" || dd if=/dev/zero of="$SWAPFILE" bs=1M count="${SIZE%M}"
chmod 600 "$SWAPFILE"
mkswap "$SWAPFILE"
swapon "$SWAPFILE"

if ! grep -q "$SWAPFILE" /etc/fstab; then
    echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab
    echo "Added swap to /etc/fstab (persists across reboots)"
fi

echo ""
echo "Done! Swap active:"
free -m
