# rexasub

این مخزن برای دریافت، استخراج و ذخیره‌سازی آی‌پی‌های استخراج‌شده از لینک‌های اشتراک (Subscription) طراحی شده است. این پروژه برای کار با لینک‌های Cloudflare، VLESS، VMess و سرویس‌های مشابه قابل استفاده است.

## امکانات

- دریافت خودکار محتوای لینک اشتراک از یک URL
- پشتیبانی از داده‌های متنی و Base64
- استخراج آی‌پی‌ها از لینک‌های VLESS/VMess و مقادیر host/sni/add
- ذخیره‌سازی خودکار در فایل ips.txt
- اجرای خودکار هر دقیقه با GitHub Actions

## ساختار پروژه

- scripts/fetch_ips.py: اسکریپت اصلی برای دریافت و استخراج آی‌پی‌ها
- .github/workflows/fetch-ips.yml: workflow برنامه‌ریزی‌شده برای اجرای هر دقیقه
- tests/: تست‌های پوشش‌دهنده‌ی منطق استخراج
- ips.txt: خروجی ثبت‌شده‌ی آی‌پی‌ها با زمان

## نحوه اجرا

1. کلون کردن مخزن
   ```bash
   git clone https://github.com/Rexa00/rexasub.git
   cd rexasub
   ```

2. اجرای اسکریپت
   ```bash
   python scripts/fetch_ips.py
   ```

3. اجرای تست‌ها
   ```bash
   python -m unittest discover -s tests -v
   ```

## خروجی

فایل ips.txt شامل سطرهای زیر است:

```text
timestamp    ip
```

هر سطر شامل زمان UTC و آی‌پی استخراج‌شده است.

## GitHub Actions

workflow در مسیر .github/workflows/fetch-ips.yml به‌صورت خودکار هر دقیقه اجرا می‌شود و در صورت وجود تغییر، آن را در مخزن ثبت می‌کند.

## نکته

اگر لینک اشتراک شما شامل دامنه‌های Cloudflare یا hostnames باشد، اسکریپت تلاش می‌کند آن‌ها را به آی‌پی حل کند و در خروجی ثبت نماید.
