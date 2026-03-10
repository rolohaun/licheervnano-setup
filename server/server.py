#!/usr/bin/env python3
"""LicheeRV Nano device stats web server."""

import http.server
import os
import time

PORT = 8080


def read_file(path, default="N/A"):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return default


def get_uptime():
    data = read_file("/proc/uptime")
    try:
        secs = float(data.split()[0])
        days = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins = int((secs % 3600) // 60)
        s = int(secs % 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        parts.append(f"{mins}m {s}s")
        return " ".join(parts)
    except Exception:
        return data


def get_memory():
    data = read_file("/proc/meminfo")
    mem = {}
    for line in data.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            mem[parts[0].rstrip(":")] = int(parts[1])
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", 0)
    used = total - available
    pct = (used / total * 100) if total else 0
    return {
        "total_mb": total // 1024,
        "used_mb": used // 1024,
        "free_mb": available // 1024,
        "pct": round(pct, 1),
    }


def get_cpu_usage():
    def read_stat():
        line = read_file("/proc/stat").splitlines()[0]
        vals = list(map(int, line.split()[1:]))
        idle = vals[3]
        total = sum(vals)
        return idle, total

    idle1, total1 = read_stat()
    time.sleep(0.2)
    idle2, total2 = read_stat()
    diff_idle = idle2 - idle1
    diff_total = total2 - total1
    usage = (1 - diff_idle / diff_total) * 100 if diff_total else 0
    return round(usage, 1)


def get_load():
    data = read_file("/proc/loadavg")
    parts = data.split()
    return parts[0], parts[1], parts[2]


def get_cpu_temp():
    paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/devices/virtual/thermal/thermal_zone0/temp",
    ]
    for p in paths:
        val = read_file(p, None)
        if val:
            try:
                return f"{int(val) / 1000:.1f} °C"
            except Exception:
                pass
    return "N/A"


def get_os_info():
    uname = os.uname()
    return {
        "hostname": uname.nodename,
        "kernel": uname.release,
        "arch": uname.machine,
    }


def get_disk():
    try:
        st = os.statvfs("/")
        total = st.f_blocks * st.f_frsize
        free = st.f_bfree * st.f_frsize
        used = total - free
        pct = round(used / total * 100, 1) if total else 0
        return {
            "total_mb": total // (1024 * 1024),
            "used_mb": used // (1024 * 1024),
            "free_mb": free // (1024 * 1024),
            "pct": pct,
        }
    except Exception:
        return {"total_mb": 0, "used_mb": 0, "free_mb": 0, "pct": 0}


def bar(pct, color):
    return f"""
    <div class="bar-bg">
      <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
    </div>"""


def build_html():
    os_info = get_os_info()
    uptime = get_uptime()
    load1, load5, load15 = get_load()
    cpu = get_cpu_usage()
    temp = get_cpu_temp()
    mem = get_memory()
    disk = get_disk()

    cpu_color = "#e74c3c" if cpu > 80 else "#f39c12" if cpu > 50 else "#2ecc71"
    mem_color = "#e74c3c" if mem["pct"] > 80 else "#f39c12" if mem["pct"] > 50 else "#3498db"
    disk_color = "#e74c3c" if disk["pct"] > 80 else "#f39c12" if disk["pct"] > 50 else "#9b59b6"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="60">
  <title>{os_info['hostname']} — Stats</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0f1117;
      color: #e0e0e0;
      min-height: 100vh;
      padding: 24px 16px;
    }}
    h1 {{
      font-size: 1.4rem;
      font-weight: 600;
      color: #fff;
      margin-bottom: 4px;
    }}
    .subtitle {{
      font-size: 0.8rem;
      color: #666;
      margin-bottom: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
      max-width: 900px;
    }}
    .card {{
      background: #1a1d27;
      border: 1px solid #2a2d3a;
      border-radius: 12px;
      padding: 18px 20px;
    }}
    .card-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #666;
      margin-bottom: 8px;
    }}
    .card-value {{
      font-size: 1.6rem;
      font-weight: 700;
      color: #fff;
      line-height: 1;
      margin-bottom: 10px;
    }}
    .card-sub {{
      font-size: 0.75rem;
      color: #888;
      margin-top: 6px;
    }}
    .bar-bg {{
      height: 6px;
      background: #2a2d3a;
      border-radius: 3px;
      overflow: hidden;
      margin-top: 10px;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 3px;
      transition: width 0.4s ease;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      color: #aaa;
      margin-top: 6px;
    }}
    .badge {{
      display: inline-block;
      background: #2a2d3a;
      border-radius: 6px;
      padding: 3px 8px;
      font-size: 0.72rem;
      color: #aaa;
      margin-top: 8px;
    }}
    .refresh-note {{
      font-size: 0.7rem;
      color: #444;
      margin-top: 20px;
    }}
  </style>
</head>
<body>
  <h1>&#127762; {os_info['hostname']}</h1>
  <p class="subtitle">LicheeRV Nano &mdash; refreshes every 60s</p>

  <div class="grid">

    <div class="card">
      <div class="card-label">System</div>
      <div class="card-value" style="font-size:1rem">{os_info['hostname']}</div>
      <div class="badge">{os_info['kernel']}</div>
      <div class="badge">{os_info['arch']}</div>
      <div class="card-sub">Uptime: {uptime}</div>
    </div>

    <div class="card">
      <div class="card-label">CPU Usage</div>
      <div class="card-value" style="color:{cpu_color}">{cpu}%</div>
      {bar(cpu, cpu_color)}
      <div class="info-row">
        <span>Load: {load1} {load5} {load15}</span>
        <span>Temp: {temp}</span>
      </div>
    </div>

    <div class="card">
      <div class="card-label">Memory</div>
      <div class="card-value" style="color:{mem_color}">{mem['pct']}%</div>
      {bar(mem['pct'], mem_color)}
      <div class="info-row">
        <span>Used: {mem['used_mb']} MB</span>
        <span>Free: {mem['free_mb']} MB</span>
        <span>Total: {mem['total_mb']} MB</span>
      </div>
    </div>

    <div class="card">
      <div class="card-label">Disk ( / )</div>
      <div class="card-value" style="color:{disk_color}">{disk['pct']}%</div>
      {bar(disk['pct'], disk_color)}
      <div class="info-row">
        <span>Used: {disk['used_mb']} MB</span>
        <span>Free: {disk['free_mb']} MB</span>
        <span>Total: {disk['total_mb']} MB</span>
      </div>
    </div>

  </div>

  <p class="refresh-note">Auto-refreshing every 60 seconds</p>
</body>
</html>"""


class StatsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        html = build_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, fmt, *args):
        pass  # silence request logs


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), StatsHandler)
    print(f"Stats server running on http://0.0.0.0:{PORT}")
    server.serve_forever()
