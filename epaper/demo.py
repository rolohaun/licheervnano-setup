#!/usr/bin/env python3
"""
Display device stats on a Waveshare 4.2" e-Paper (Rev 2.1).
Run from /opt/epaper:  python3 demo.py
"""

import os
import sys
import time
import socket
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import epd4in2_V2 as epd_module

W = epd_module.EPD_WIDTH   # 400
H = epd_module.EPD_HEIGHT  # 300

# ── font helpers ─────────────────────────────────────────────────────────────

FONT_SEARCH = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def find_font():
    for p in FONT_SEARCH:
        if os.path.exists(p):
            return p
    return None


def make_font(size):
    path = find_font()
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ── system stats ─────────────────────────────────────────────────────────────

def read_file(path, default="N/A"):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return default


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "no network"


def get_uptime():
    try:
        secs = float(read_file("/proc/uptime").split()[0])
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        parts = []
        if d: parts.append(f"{d}d")
        if h: parts.append(f"{h}h")
        parts.append(f"{m}m")
        return " ".join(parts)
    except Exception:
        return "N/A"


def get_cpu():
    def read_stat():
        line = read_file("/proc/stat").splitlines()[0]
        vals = list(map(int, line.split()[1:]))
        return vals[3], sum(vals)
    idle1, tot1 = read_stat()
    time.sleep(0.3)
    idle2, tot2 = read_stat()
    dt = tot2 - tot1
    return round((1 - (idle2 - idle1) / dt) * 100, 1) if dt else 0.0


def get_mem():
    data = read_file("/proc/meminfo")
    m = {}
    for line in data.splitlines():
        p = line.split()
        if len(p) >= 2:
            m[p[0].rstrip(":")] = int(p[1])
    total = m.get("MemTotal", 0)
    avail = m.get("MemAvailable", 0)
    used  = total - avail
    swap_total = m.get("SwapTotal", 0)
    swap_used  = swap_total - m.get("SwapFree", 0)
    return (used // 1024, total // 1024, swap_used // 1024, swap_total // 1024)


def get_temp():
    for p in ("/sys/class/thermal/thermal_zone0/temp",
              "/sys/devices/virtual/thermal/thermal_zone0/temp"):
        v = read_file(p, None)
        if v:
            try:
                return f"{int(v)/1000:.1f}C"
            except Exception:
                pass
    return "N/A"


# ── draw ─────────────────────────────────────────────────────────────────────

def draw_bar(draw, x, y, w, h, pct, fill=0):
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=0, fill=255)
    filled_w = int(w * min(pct, 100) / 100)
    if filled_w:
        draw.rectangle([x, y, x + filled_w - 1, y + h - 1], fill=fill)


def build_image():
    hostname = os.uname().nodename
    kernel   = os.uname().release
    ip       = get_ip()
    uptime   = get_uptime()
    cpu      = get_cpu()
    temp     = get_temp()
    mem_used, mem_total, swap_used, swap_total = get_mem()
    mem_pct  = round(mem_used / mem_total * 100, 1) if mem_total else 0
    swap_pct = round(swap_used / swap_total * 100, 1) if swap_total else 0
    now      = time.strftime("%Y-%m-%d %H:%M")

    img  = Image.new('1', (W, H), 255)   # white background
    draw = ImageDraw.Draw(img)

    fL = make_font(22)   # large
    fM = make_font(16)   # medium
    fS = make_font(13)   # small

    # ── header ───────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 34], fill=0)
    draw.text((8, 6),  hostname,       font=fL, fill=255)
    draw.text((W - 130, 10), kernel,   font=fS, fill=255)

    y = 42
    # ── IP / uptime ──────────────────────────────────────────────────────────
    draw.text((8,  y), f"IP:     {ip}",       font=fM, fill=0)
    draw.text((8,  y + 22), f"Uptime: {uptime}",    font=fM, fill=0)

    y += 54
    draw.line([(0, y), (W, y)], fill=0, width=1)
    y += 6

    # ── CPU ──────────────────────────────────────────────────────────────────
    draw.text((8, y), f"CPU  {cpu}%   {temp}", font=fM, fill=0)
    draw_bar(draw, 8, y + 22, W - 16, 10, cpu)
    y += 42

    # ── RAM ──────────────────────────────────────────────────────────────────
    draw.text((8, y), f"RAM  {mem_pct}%   ({mem_used}/{mem_total} MB)", font=fM, fill=0)
    draw_bar(draw, 8, y + 22, W - 16, 10, mem_pct)
    y += 42

    # ── Swap ─────────────────────────────────────────────────────────────────
    draw.text((8, y), f"Swap {swap_pct}%   ({swap_used}/{swap_total} MB)", font=fM, fill=0)
    draw_bar(draw, 8, y + 22, W - 16, 10, swap_pct)
    y += 42

    draw.line([(0, y), (W, y)], fill=0, width=1)

    # ── timestamp ────────────────────────────────────────────────────────────
    draw.text((8, H - 22), f"Updated: {now}", font=fS, fill=0)

    return img


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Initialising e-Paper display...", flush=True)
    epd = epd_module.EPD()

    if epd.init() != 0:
        print("EPD init failed — check wiring and SPI bus.", file=sys.stderr)
        sys.exit(1)

    print("Clearing display...", flush=True)
    epd.Clear()

    print("Drawing stats...", flush=True)
    img = build_image()
    epd.display(epd.getbuffer(img))

    print("Done. Putting display to sleep.", flush=True)
    epd.sleep()


if __name__ == "__main__":
    main()
