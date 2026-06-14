#!/usr/bin/env python3
"""
ALIRZWIRUS AUTO-LAUNCHER ENGINE v6.0
Cross-Platform Telegram MTProto Proxy Tool
Supports: Android (Termux) | Linux | macOS | Windows
Offline Cache Mode: works even when internet is blocked
"""

import os
import re
import sys
import html
import json
import time
import shutil
import socket
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

# ─── ANSI Colors (disabled on Windows without VT support) ────────────────────
def _supports_color():
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOR = _supports_color()

def _c(code):
    return code if _COLOR else ""

R    = _c('\033[31m')
G    = _c('\033[32m')
Y    = _c('\033[33m')
B    = _c('\033[34m')
P    = _c('\033[35m')
C    = _c('\033[36m')
GRA  = _c('\033[90m')
W    = _c('\033[0m')
BOLD = _c('\033[1m')

# ─── Config ──────────────────────────────────────────────────────────────────
VERSION         = "6.0"
CACHE_FILE      = Path.home() / ".alirzwirus_cache.json"
CACHE_MAX_AGE_H = 72    # hours before cache is considered expired
AUTO_REFRESH_H  = 6     # background refresh interval in hours

CHANNELS = [
    "ProxyMTProto", "TelMTProto", "MTProtoProxies",
    "Proxy_MTProto_Telegram", "bestMTProto", "MTProto_Proxy",
    "MTProto_Proxy_List", "mtrproxytg", "proxyforopera",
    "proxy_shadosocks", "freev2ray",
]

# ─── Banner ──────────────────────────────────────────────────────────────────
BANNER = f"""
{P} █████╗ ██╗     ██╗██████╗ ███████╗{W}
{P}██╔══██╗██║     ██║██╔══██╗╚══███╔╝{W}
{P}███████║██║     ██║██████╔╝  ███╔╝ {W}
{P}██╔══██║██║     ██║██╔══██╗ ███╔╝  {W}
{P}██║  ██║███████╗██║██║  ██║███████╗{W}
{P}╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝╚══════╝{W}
{C}          V I R U S{W}
{GRA}┌──────────────────────────────────────────────────────────┐
│{W}  Codename : ALIRZWIRUS AUTO-LAUNCHER ENGINE v{VERSION}        {GRA}│
│{W}  Feature  : Offline Cache · Auto Refresh · Smart Mode    {GRA}│
│{W}  Platform : Android · Linux · macOS · Windows            {GRA}│
│{W}  Author   : alirzwirus                                   {GRA}│
└──────────────────────────────────────────────────────────┘{W}
"""

# ─── Platform ────────────────────────────────────────────────────────────────
def detect_platform():
    if os.environ.get("TERMUX_VERSION") or shutil.which("am"):
        return "android"
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"

def clear_screen():
    os.system("cls" if sys.platform == "win32" else "clear")

# ─── Cache ───────────────────────────────────────────────────────────────────
def cache_save(proxies):
    data = {
        "version"  : VERSION,
        "saved_at" : datetime.now().isoformat(),
        "count"    : len(proxies),
        "proxies"  : proxies,
    }
    try:
        CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"{Y}[!] Cache save failed: {e}{W}")

def cache_load():
    """Returns (proxies: list, age_hours: float|None)"""
    if not CACHE_FILE.exists():
        return [], None
    try:
        data      = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        saved_at  = datetime.fromisoformat(data["saved_at"])
        age_hours = (datetime.now() - saved_at).total_seconds() / 3600
        return data.get("proxies", []), age_hours
    except Exception:
        return [], None

def cache_status(age_hours):
    if age_hours is None:
        return f"{R}[CACHE] Empty{W}"
    h = int(age_hours)
    if age_hours < 6:
        return f"{G}[CACHE] Fresh ({h}h ago){W}"
    if age_hours < 24:
        return f"{Y}[CACHE] Usable ({h}h ago){W}"
    if age_hours < CACHE_MAX_AGE_H:
        return f"{Y}[CACHE] Old ({h}h ago){W}"
    return f"{R}[CACHE] Expired ({h}h ago){W}"

# ─── Network ─────────────────────────────────────────────────────────────────
def is_internet_up(timeout=2.0):
    """Test connectivity using direct IP — bypasses DNS filtering."""
    endpoints = [
        ("8.8.8.8",        53),
        ("1.1.1.1",        53),
        ("208.67.222.222", 53),
        ("9.9.9.9",        53),
    ]
    for host, port in endpoints:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False

def dns_check():
    results = {}
    for host in ["t.me", "telegram.org", "google.com"]:
        try:
            ip = socket.getaddrinfo(host, 443)[0][4][0]
            results[host] = (True, ip)
        except Exception:
            results[host] = (False, "FAIL")
    return results

def is_telegram_reachable(proxy_url=None, timeout=6.0):
    try:
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        r = requests.get(
            "https://t.me",
            headers={"User-Agent": "Mozilla/5.0"},
            proxies=proxies,
            timeout=timeout,
            allow_redirects=True,
        )
        return r.status_code < 500
    except Exception:
        return False

# ─── Proxy Detection ─────────────────────────────────────────────────────────
def detect_system_proxy():
    """Detect proxy from env vars or common local ports."""
    for var in ["HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY"]:
        val = os.environ.get(var)
        if val:
            if not val.startswith(("http://", "https://", "socks")):
                val = f"http://{val}"
            return ("env", val)
    common_ports = [20808, 10809, 7890, 2081, 1080, 8118, 8080, 3128, 9090]
    for port in common_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    return ("port", f"http://127.0.0.1:{port}")
        except Exception:
            continue
    return (None, None)

def ask_manual_proxy():
    try:
        inp = input(
            f"{Y}[?] Enter proxy URL (e.g. http://127.0.0.1:8080) or press Enter to skip: {W}"
        ).strip()
        if inp:
            if not inp.startswith(("http://", "https://", "socks")):
                inp = f"http://{inp}"
            return inp
    except (KeyboardInterrupt, EOFError):
        pass
    return None

def check_tg_handler(platform):
    if platform in ("android", "windows"):
        return True
    try:
        r = subprocess.run(
            ["xdg-mime", "query", "default", "x-scheme-handler/tg"],
            capture_output=True, text=True, timeout=2,
        )
        return bool(r.stdout.strip())
    except Exception:
        return False

# ─── Harvester ───────────────────────────────────────────────────────────────
def harvest_channel(channel, proxy_url):
    url     = f"https://t.me/s/{channel}"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    try:
        kwargs = {"headers": headers, "timeout": 12}
        if proxy_url:
            kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
        resp = requests.get(url, **kwargs)
        if resp.status_code != 200:
            return []
        pattern = r'(?:tg://proxy\?[^\s<>"]+)|(?:https://t\.me/proxy\?[^\s<>"]+)'
        found   = re.findall(pattern, resp.text)
        cleaned = []
        for link in found:
            clean = unquote(html.unescape(link)).replace("https://t.me/", "tg://")
            cleaned.append(clean)
        return cleaned
    except Exception:
        return []

def harvest_all(proxy_url):
    all_proxies = []
    total = len(CHANNELS)
    print(f"\n{C}[->] Scanning {total} channels...{W}\n")
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(harvest_channel, ch, proxy_url): ch for ch in CHANNELS}
        done = 0
        for fut in as_completed(futs):
            ch   = futs[fut]
            res  = fut.result()
            done += 1
            bar  = G + ("=" * done) + GRA + ("-" * (total - done)) + W
            if res:
                print(f"  {G}[+{len(res):02d}]{W}  {ch:<28}  [{bar}{GRA}]{W}")
            else:
                print(f"  {GRA}[  ]{W}  {ch:<28}  [{bar}{GRA}]{W}")
            all_proxies.extend(res)
    return sorted(set(all_proxies))

# ─── Auto Refresh ─────────────────────────────────────────────────────────────
def start_background_refresh(proxy_url):
    def _job():
        while True:
            time.sleep(AUTO_REFRESH_H * 3600)
            if is_internet_up():
                proxies = harvest_all(proxy_url)
                if proxies:
                    cache_save(proxies)
    t = threading.Thread(target=_job, daemon=True)
    t.start()

# ─── Launcher ────────────────────────────────────────────────────────────────
def open_link(link, platform):
    if platform == "android":
        os.system(f"am start -a android.intent.action.VIEW -d '{link}' >/dev/null 2>&1")
    elif platform == "windows":
        os.startfile(link)  # type: ignore[attr-defined]
    elif platform == "macos":
        os.system(f"open '{link}' >/dev/null 2>&1")
    else:
        os.system(f"xdg-open '{link}' >/dev/null 2>&1")

def extract_field(link, key):
    m = re.search(rf"{key}=([^&]+)", link)
    return m.group(1) if m else "?"

# ─── Browser UI ──────────────────────────────────────────────────────────────
def browse_proxies(proxies, platform, from_cache, cache_age):
    total = len(proxies)
    print(f"\n{P}{'=' * 62}{W}")
    if from_cache and cache_age is not None:
        print(f"{Y}  [OFFLINE MODE]  Using cached proxies ({int(cache_age)}h ago){W}")
    else:
        print(f"{G}  [ONLINE MODE]   {BOLD}{total}{W}{G} unique proxies loaded{W}")
    print(f"{P}{'=' * 62}{W}")
    print(f"  {Y}[Enter]{W} or {Y}[o]{W} = open in Telegram  |  {Y}[s]{W} = save  |  {Y}[q]{W} = quit\n")

    for idx, link in enumerate(proxies, 1):
        server = extract_field(link, "server")
        port   = extract_field(link, "port")
        print(f"  {C}[{idx:02d}/{total}]{W}  {G}{server:<36}{W}  {GRA}port:{port}{W}")
        try:
            cmd = input(f"  {GRA}|>{W} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{R}[!] Stopped.{W}")
            break

        if cmd == "q":
            print(f"\n{R}[!] Quit by user.{W}")
            break
        if cmd in ("o", ""):
            open_link(link, platform)
            print(f"  {G}  -> Link opened in Telegram{W}")
        if cmd == "s":
            ts   = int(time.time())
            path = f"alirzwirus_proxies_{ts}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(l + "\n" for l in proxies)
            print(f"  {G}  -> Saved: {path}{W}")
        print(f"  {GRA}{'-' * 58}{W}")

# ─── Section Header ──────────────────────────────────────────────────────────
def section(title):
    pad = 52 - len(title)
    print(f"\n{GRA}+-- {W}{BOLD}{title}{W} {GRA}{'-' * pad}+{W}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    clear_screen()
    print(BANNER)

    platform = detect_platform()
    print(f"{B}[*] Platform: {G}{platform.upper()}{W}")

    if not check_tg_handler(platform) and platform not in ("android", "windows"):
        print(f"{Y}[!] Telegram tg:// handler not detected{W}")

    # DNS check
    section("DNS Check")
    for host, (ok, ip) in dns_check().items():
        icon  = G + "[OK]" + W if ok else R + "[XX]" + W
        print(f"  {icon}  {B}{host:<20}{W}  {G if ok else R}{ip}{W}")

    # Internet connectivity
    section("Internet Connectivity")
    online = is_internet_up()
    if online:
        print(f"  {G}[OK]  Global internet reachable{W}")
    else:
        print(f"  {R}[XX]  Global internet is DOWN (national filtering?){W}")

    # Cache status
    section("Local Cache")
    cached_proxies, cache_age = cache_load()
    print(f"  {cache_status(cache_age)}")
    if cached_proxies:
        print(f"  {GRA}     {len(cached_proxies)} proxies stored in: {CACHE_FILE}{W}")

    # System proxy
    section("System Proxy")
    proxy_type, proxy_url = detect_system_proxy()
    if proxy_url:
        src = "env var" if proxy_type == "env" else f"port {proxy_url.split(':')[-1]}"
        print(f"  {G}[OK]  Proxy detected ({src}): {proxy_url}{W}")
    else:
        print(f"  {Y}[--]  No system proxy detected{W}")
        if online:
            manual = ask_manual_proxy()
            if manual:
                proxy_url  = manual
                proxy_type = "manual"
                print(f"  {G}[OK]  Using manual proxy: {proxy_url}{W}")

    print(f"\n{GRA}{'=' * 62}{W}\n")

    # ── Decision: online or offline ──────────────────────────────────────────
    if not online:
        # OFFLINE MODE
        print(f"{Y}{'*' * 62}{W}")
        print(f"{Y}  ** OFFLINE MODE ACTIVATED **{W}")
        print(f"{Y}{'*' * 62}{W}")

        if not cached_proxies:
            print(f"\n{R}  [!!] Cache is empty — no proxies available offline!{W}")
            print(f"\n{Y}  Solution:{W}")
            print(f"  {W}  1. Run this script once while you have internet")
            print(f"  {W}  2. Proxies will be saved automatically")
            print(f"  {W}  3. Next time it works even without internet\n")
            return

        if cache_age and cache_age > CACHE_MAX_AGE_H:
            print(f"\n{R}  [!] Cache is very old ({int(cache_age)}h) — some proxies may be dead{W}")

        browse_proxies(cached_proxies, platform, from_cache=True, cache_age=cache_age)
        all_proxies = cached_proxies

    else:
        # ONLINE MODE
        use_cache = False
        if cached_proxies and cache_age is not None and cache_age < AUTO_REFRESH_H:
            try:
                ans = input(
                    f"{Y}[?] Cache is fresh ({int(cache_age)}h ago). Use cache instead of re-harvesting? [y/N]: {W}"
                ).strip().lower()
                use_cache = (ans == "y")
            except (KeyboardInterrupt, EOFError):
                use_cache = True

        if use_cache:
            all_proxies = cached_proxies
        else:
            tg_up = is_telegram_reachable(proxy_url)
            if not tg_up:
                msg = f"even with proxy {proxy_url}" if proxy_url else "directly (it may be filtered)"
                print(f"{Y}[!] Telegram not reachable {msg} — attempting harvest anyway...{W}")

            all_proxies = harvest_all(proxy_url)

            if all_proxies:
                cache_save(all_proxies)
                print(f"\n{G}[OK] {len(all_proxies)} proxies saved -> {CACHE_FILE}{W}")
                start_background_refresh(proxy_url)
            elif cached_proxies:
                print(f"\n{Y}[!] Harvest returned nothing — falling back to cache{W}")
                all_proxies = cached_proxies
                use_cache   = True
            else:
                print(f"\n{R}[XX] No proxies found and cache is empty!{W}")
                print(f"{Y}[!] Try: http_proxy=YOUR_PROXY python3 alirzwirus.py{W}\n")
                return

        browse_proxies(
            all_proxies,
            platform,
            from_cache=use_cache,
            cache_age=cache_age if use_cache else 0.0,
        )

    # Final auto-save
    ts   = int(time.time())
    path = f"alirzwirus_proxies_{ts}.txt"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(l + "\n" for l in all_proxies)
        print(f"\n{G}[OK] Full list saved -> {path}{W}")
    except Exception:
        pass

    total = len(all_proxies)
    print(f"\n{P}{'=' * 62}{W}")
    print(f"{P}  *** MISSION COMPLETE — {total} proxies processed ***{W}")
    print(f"{P}{'=' * 62}{W}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Interrupted.{W}")
    except Exception as e:
        print(f"\n{R}[!!] Unexpected error: {e}{W}")