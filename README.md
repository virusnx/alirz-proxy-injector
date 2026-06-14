<div align="center">

```
 █████╗ ██╗     ██╗██████╗ ███████╗
██╔══██╗██║     ██║██╔══██╗╚══███╔╝
███████║██║     ██║██████╔╝  ███╔╝ 
██╔══██║██║     ██║██╔══██╗ ███╔╝  
██║  ██║███████╗██║██║  ██║███████╗
╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝╚══════╝
          W I R U S
```

# alirz-proxy-injector

**Cross-Platform Telegram MTProto Proxy Tool**  
Auto-harvest · Offline Cache · Smart Detection · One-click Inject

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square)](https://github.com/virusnx/alirz-proxy-injector)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-6.0-purple?style=flat-square)](https://github.com/virusnx/alirz-proxy-injector)

</div>

---

## What is this?

**alirz-proxy-injector** automatically harvests MTProto proxies from public Telegram channels and injects them directly into the Telegram app — with a single keypress.

The key feature: it works **even when the internet is completely blocked**.  
It saves proxies locally so when your connection drops (national filtering, outages, restrictions), you still have a fresh list ready to go.

---

## Features

| Feature | Description |
|---|---|
| **Offline Cache Mode** | Saves proxies to disk — works without internet |
| **Smart Connectivity Check** | Detects global internet vs national network using direct IP |
| **Auto Background Refresh** | Refreshes cache every 6h while online |
| **System Proxy Detection** | Auto-detects VPN/proxy from env vars or local ports |
| **Multi-Channel Harvest** | Scans 11 Telegram channels in parallel |
| **One-Click Inject** | Opens MTProto link directly in Telegram |
| **Cross-Platform** | Android, Linux, macOS, Windows |

---

## How Offline Mode Works

```
Script starts
      │
      ├─ Global internet reachable?
      │         │
      │         ├── YES ──► Harvest from Telegram channels
      │         │           ──► Save to local cache
      │         │           ──► Display & inject
      │         │           ──► Background refresh every 6h
      │         │
      │         └── NO  ──► Load from local cache (~/.alirzwirus_cache.json)
      │                     ──► Display & inject  ✔
      │                     ──► Cache empty? ──► Instructions shown
```

> **Tip:** Run the script at least once while you have internet.  
> The cache stays valid for up to **72 hours**.

---

## Installation

```bash
git clone https://github.com/virusnx/alirz-proxy-injector.git
cd alirz-proxy-injector
pip install -r requirements.txt
```

### Android (Termux)

```bash
pkg update && pkg install python
pip install requests
python alirzwirus.py
```

---

## Usage

```bash
python alirzwirus.py
```

With a manual proxy:

```bash
http_proxy=http://127.0.0.1:8080 python alirzwirus.py
# or
HTTPS_PROXY=socks5://127.0.0.1:1080 python alirzwirus.py
```

### Controls

| Key | Action |
|-----|--------|
| `Enter` or `o` | Open proxy in Telegram |
| `s` | Save full list to `.txt` file |
| `q` | Quit |

---

## Cache Location

| Platform | Path |
|---|---|
| Linux / macOS | `~/.alirzwirus_cache.json` |
| Windows | `C:\Users\YOU\.alirzwirus_cache.json` |
| Android (Termux) | `/data/data/com.termux/files/home/.alirzwirus_cache.json` |

---

## Supported Platforms

| Platform | Open Method |
|---|---|
| Android (Termux) | `am start` intent |
| Linux | `xdg-open` |
| macOS | `open` |
| Windows | `os.startfile` |

---

## Proxy Sources

Harvests MTProto proxy links from 11 public Telegram channels in parallel:

`ProxyMTProto` · `TelMTProto` · `MTProtoProxies` · `Proxy_MTProto_Telegram`  
`bestMTProto` · `MTProto_Proxy` · `MTProto_Proxy_List` · `mtrproxytg`  
`proxyforopera` · `proxy_shadosocks` · `freev2ray`

---

## Project Structure

```
alirz-proxy-injector/
├── alirzwirus.py      # main script (v6.0)
├── requirements.txt   # dependencies (requests)
├── .gitignore
└── README.md
```

---

## Requirements

- Python **3.9+**
- `requests` — only external dependency

---

<div align="center">

**Made by [alirzwirus](https://github.com/virusnx)**

</div>