# ALIRZ Auto-Launcher Engine v5.1

**Cross-Platform Telegram MTProto Proxy Injector** — Android + Linux / macOS

موتور خودکار استخراج و تزریق پروکسی تلگرام — کراس پلتفرم (اندروید + لینوکس)

---

## قابلیت‌ها / Features

- **استخراج خودکار** پروکسی MTProto از کانال‌های تلگرام (۷ کانال فعال)
- **تشخیص هوشمند پروکسی** — اول environment variable رو چک میکنه، بعد پورت‌های لوکال (V2Ray, Clash, etc.)
- **کراس پلتفرم** — اندروید (Termux) و لینوکس/مک (Desktop Telegram)
- **تزریق مستقیم** به اپلیکیشن تلگرام — `am start` برای اندروید، `xdg-open` برای لینوکس
- **ذخیره خودکار** لیست پروکسی‌ها در فایل
- **DNS diagnostic** — نمایش وضعیت resolve شدن Telegram

## نصب / Installation

```bash
git clone https://github.com/alirzwirus/alirz-proxy-injector.git
cd alirz-proxy-injector
pip install -r requirements.txt
```

### وابستگی‌ها / Dependencies

- Python 3.7+
- `requests` (تنها کتابخونه خارجی / only external library)

## اجرا / Usage

```bash
python3 script.py
```

اگر پروکسی شما به صورت environment variable ست شده، خودکار تشخیص میده:

```bash
# مثال: اگر از proxy tool استفاده میکنی
export HTTP_PROXY=http://127.0.0.1:8080
python3 script.py

# یا یک خطی
http_proxy=http://127.0.0.1:8080 python3 script.py
```

### دستورات حین اجرا / Commands

| Key | Function |
|-----|----------|
| `Enter` | پروکسی بعدی / Next proxy |
| `q` | خروج / Quit |
| `s` | ذخیره لیست / Save list |

## ساختار پروژه / Project Structure

```
├── script.py          # main script
├── requirements.txt   # dependencies
└── README.md          # this file
```

## پلتفرم‌های پشتیبانی شده / Supported Platforms

| Platform | Method |
|----------|--------|
| **Android (Termux)** | `am start` |
| **Linux Desktop** | `xdg-open` |
| **macOS** | `open` (via xdg-open) |

## نکته مهم / Important Note

برخی از کانال‌های تلگرام ممکن است فیلتر شده باشند و نیاز به VPN یا پروکسی داشته باشید. اسکریپت به طور خودکار از `HTTP_PROXY` environment variable استفاده میکند.‌

Some Telegram channels may be blocked and require VPN/proxy access. The script automatically uses the `HTTP_PROXY` environment variable.

---

**Developed by: alirzwirus**
