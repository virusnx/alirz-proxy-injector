#!/usr/bin/env python3
"""
ALIRZ AUTO-LAUNCHER ENGINE v5.1
Cross-Platform Telegram Proxy Injector — Android + Linux / macOS
"""

import requests
import re
import socket
import os
import html
import time
import sys
import shutil
import subprocess
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
B = '\033[34m'
P = '\033[35m'
C = '\033[36m'
GRA = '\033[90m'
W = '\033[0m'
BOLD = '\033[1m'

BANNER = f"""
{P}▒█▀▄▀█ ░█▀▀█ ░█▀▀▀ ▒█░▄▀ ▀▀█▀▀ ▒█▄░▒█ ▒█▀▀█
▒█▒█▒█ ▒█▄▄█ ▒█▀▀▀ ▒█▀▄─ ░▒█░░ ▒█▒█▒█ ▒█─▄▄
▒█░░▒█ ▒█░░░ ▒█▄▄▄ ▒█░▒█ ▄▄█▄▄ ▒█░░▀█ ▒█▄▄█{W}
{C}          ═══ ALIRZ AUTO-LAUNCHER ENGINE v5.1 ═══{W}
{GRA}┌────────────────────────────────────────────────────────────┐
│ {W}Codename:    ALIRZ CROSS-PLATFORM INJECTOR               {GRA}│
│ {W}Powered By:   alirzwirus                            {GRA}│
│ {W}Compatibility: Android | Linux | macOS                     {GRA}│
└────────────────────────────────────────────────────────────┘{W}
"""

_DATABASE_TARGETS = [
    "ProxyMTProto", "TelMTProto", "MTProtoProxies",
    "Proxy_MTProto_Telegram", "bestMTProto", "MTProto_Proxy",
    "MTProto_Proxy_List",
]

def detect_platform():
    if os.environ.get('TERMUX_VERSION') or shutil.which('am'):
        return 'android'
    return 'linux'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def detect_proxy():
    for var in ['HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy', 'ALL_PROXY', 'all_proxy']:
        val = os.environ.get(var)
        if val:
            if not val.startswith(('http://', 'https://', 'socks')):
                val = f"http://{val}"
            return ('env', val)
    ports = [20808, 10809, 7890, 2081, 1080, 8118, 8080, 3128, 8888, 9090]
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex(('127.0.0.1', port)) == 0:
                    return ('port', f"http://127.0.0.1:{port}")
        except:
            continue
    return (None, None)

def resolve_diagnostic():
    results = {}
    for host in ['t.me', 'telegram.org', 'google.com']:
        try:
            ip = socket.getaddrinfo(host, 443)[0][4][0]
            results[host] = ip
        except Exception as e:
            results[host] = f"FAIL: {e}"
    return results

def secure_extractor(channel, proxy_url, proxy_type):
    url = f"https://t.me/s/{channel}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    try:
        if proxy_url and proxy_type:
            p = {"http": proxy_url, "https": proxy_url}
            resp = requests.get(url, headers=headers, proxies=p, timeout=12)
        else:
            resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []
        pattern = r'(?:tg:\/\/proxy\?[^\s<>"]+)|(?:https:\/\/t\.me\/proxy\?[^\s<>"]+)'
        found = re.findall(pattern, resp.text)
        cleaned = []
        for link in found:
            cleaned.append(unquote(html.unescape(link)).replace('https://t.me/', 'tg://'))
        return cleaned
    except:
        return []

def open_link(link):
    if detect_platform() == 'android':
        os.system(f"am start -a android.intent.action.VIEW -d '{link}' >/dev/null 2>&1")
    else:
        os.system(f"xdg-open '{link}' >/dev/null 2>&1")

def extract_server(link):
    m = re.search(r'server=([^&]+)', link)
    return m.group(1) if m else "Unknown-Node"

def check_telegram():
    if detect_platform() == 'android':
        return True
    try:
        r = subprocess.run(
            ['xdg-mime', 'query', 'default', 'x-scheme-handler/tg'],
            capture_output=True, text=True, timeout=2
        )
        return bool(r.stdout.strip())
    except:
        return False

def query_manual_proxy():
    try:
        inp = input(f"{Y}[?] Enter proxy URL (e.g. http://127.0.0.1:8080) or press Enter to skip: {W}").strip()
        if inp:
            if not inp.startswith(('http://', 'https://', 'socks')):
                inp = f"http://{inp}"
            return inp
    except:
        pass
    return None

def main():
    clear_screen()
    print(BANNER)

    plat = detect_platform()
    print(f"{B}[⚙] Platform: {G}{plat.upper()}{W}")

    tg_handler = check_telegram()
    if not tg_handler and plat != 'android':
        print(f"{Y}[!] Telegram tg:// handler not detected{W}")

    # DNS diagnostic
    dns = resolve_diagnostic()
    for host, ip in dns.items():
        icon = G if 'FAIL' not in ip else R
        print(f"{B}[dns] {icon}{host} -> {ip}{W}")

    # Proxy detection
    proxy_type, proxy_url = detect_proxy()
    if proxy_url:
        parts = proxy_url.split(':')
        src = 'env var' if proxy_type == 'env' else f'port {parts[-1]}'
        print(f"{G}[✔] Proxy detected ({src}): {proxy_url}{W}")
    else:
        print(f"{Y}[!] No proxy detected{W}")
        manual = query_manual_proxy()
        if manual:
            proxy_url = manual
            proxy_type = 'manual'
            print(f"{G}[✔] Using manual proxy: {proxy_url}{W}")

    print(f"{C}[➔] Harvesting {len(_DATABASE_TARGETS)} channels...{W}")
    all_proxies = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(secure_extractor, c, proxy_url, proxy_type): c for c in _DATABASE_TARGETS}
        for i, f in enumerate(as_completed(futs), 1):
            ch = futs[f]
            res = f.result()
            if res:
                print(f"{G}[+{len(res):02d}]{W} {ch}")
            all_proxies.extend(res)

    all_proxies = sorted(set(all_proxies))
    total = len(all_proxies)

    if total == 0:
        print(f"\n{R}[✖] No proxies found!{W}")
        print(f"{Y}[!] Possible reasons:{W}")
        print(f"{Y}  1. Your VPN/proxy may not route Telegram traffic{W}")
        print(f"{Y}  2. Try running with: http_proxy=YOUR_PROXY python3 script.py{W}")
        print(f"{Y}  3. Or set proxy manually when prompted next time{W}")
        return

    print(f"{G}[✔] {BOLD}{total}{W}{G} unique proxies loaded{W}")
    print(f"{GRA}{'━'*60}{W}")
    print(f"\n{P}🚀  ALIRZ AUTO-INJECTOR  🚀{W}")
    print(f"{Y}[Enter] next  |  [q] quit  |  [s] save list{W}\n")

    for idx, link in enumerate(all_proxies, 1):
        srv = extract_server(link)
        print(f"{C}[{idx:02d}/{total}]{W} → {G}{srv[:38]}{W}")
        try:
            open_link(link)
            cmd = input(f"{GRA}  └─[{W}Enter{GRA}] n|{W}q{GRA}|{W}s{GRA}: {W}").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{R}[!] Stopped.{W}")
            break
        if cmd == 'q':
            print(f"\n{R}[!] Stopped by user.{W}")
            break
        if cmd == 's':
            ts = int(time.time())
            with open(f"alirz_proxies_{ts}.txt", 'w') as f:
                for l in all_proxies:
                    f.write(l + '\n')
            print(f"{G}[✔] Saved to alirz_proxies_{ts}.txt{W}")
        print(f"{GRA}{'─'*60}{W}")

    ts = int(time.time())
    fname = f"alirz_proxies_{ts}.txt"
    with open(fname, 'w') as f:
        for l in all_proxies:
            f.write(l + '\n')
    print(f"{G}[✔] Full list saved → {fname}{W}")
    print(f"\n{P}{'═'*60}{W}")
    print(f"{P}███ MISSION COMPLETE — {total} proxies processed ███{W}")
    print(f"{P}{'═'*60}{W}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Interrupted.{W}")
    except Exception as e:
        print(f"\n{R}[✖] Error: {e}{W}")
