# 🐉 URL Info Gatherer v3.0

> **3 Başlı Ejderha** | Red Team | Purple Team | Blue Team

Web siteleri hakkında **kapsamlı bilgi** toplama aracı. HTTP, SSL, DNS, WHOIS, teknoloji tespiti, subdomain bulma, email scraping, sosyal medya tespiti ve screenshot.

---

## ✨ Özellikler (v3.0)

| Özellik | Açıklama |
|---------|----------|
| 🌐 **HTTP Bilgileri** | Status kod, sunucu, başlık, içerik uzunluğu |
| 🔒 **SSL Sertifika** | Bitiş tarihi, kalan gün, issuer bilgisi |
| 📡 **DNS Kayıtları** | A, AAAA, MX, TXT, NS, CNAME, SOA |
| 📋 **WHOIS Sorgulama** | Domain kayıt bilgileri, son kullanma tarihi |
| 🕵️ **Teknoloji Tespiti** | 25+ teknoloji (WordPress, React, Laravel, CloudFlare...) |
| 📸 **Screenshot** | Gerçek ekran görüntüsü alma |
| 🔗 **Subdomain Bulma** | DNS brute force ile alt domain keşfi |
| 📧 **Email Scraping** | Sayfadaki email adreslerini toplama |
| 📱 **Sosyal Medya** | Twitter, Instagram, GitHub, LinkedIn vb. tespiti |
| 🛡️ **Güvenlik Başlıkları** | HSTS, CSP, X-Frame-Options vb. kontrolü |
| 📊 **Raporlama** | JSON ve CSV formatlarında çıktı |
| ⚡ **Çoklu URL** | Dosyadan birden çok URL, thread desteği |

---

## 📦 Kurulum

```bash
git clone https://github.com/DobivornSec/url-info-gatherer.git
cd url-info-gatherer
pip install -r requirements.txt
```

**Gereksinimler:**
```bash
pip install requests dnspython python-whois colorama Pillow selenium webdriver-manager
```

> ⚠️ **Not:** Screenshot özelliği için sistemde Chromium/Chrome kurulu olmalı:
> ```bash
> # Kali/Debian/Ubuntu
> apt install chromium
> 
> # Chromedriver otomatik kurulur (webdriver-manager)
> ```

---

## 🚀 Kullanım

### Temel Kullanım

```bash
# Tek URL analizi
python url_info.py https://google.com

# Subdomain bulma
python url_info.py https://google.com --subdomain

# Screenshot ile
python url_info.py https://github.com --screenshot

# Tüm özellikler açık
python url_info.py https://example.com --screenshot --subdomain -o rapor.json
```

### Çoklu URL (dosyadan)

```bash
# urls.txt dosyası oluştur
echo "https://google.com" > urls.txt
echo "https://github.com" >> urls.txt

# Tüm URL'leri tara
python url_info.py -f urls.txt -t 10 --subdomain --screenshot -o sonuc.json
```

### Raporlama

```bash
# JSON rapor
python url_info.py https://google.com -o rapor.json

# CSV rapor
python url_info.py https://google.com -o rapor.csv --format csv
```

---

## 📊 Parametreler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `url` | Hedef URL | Zorunlu |
| `-f, --file` | URL listesi dosyası | Yok |
| `-o, --output` | Çıktı dosyası | Yok |
| `--format` | JSON veya CSV | `json` |
| `-t, --threads` | Thread sayısı | 5 |
| `--screenshot` | Screenshot al | Kapalı |
| `--subdomain` | Subdomain ara | Kapalı |

---

## 📁 Örnek Çıktı

```bash
╔══════════════════════════════════════════════════════════════════════════╗
║   🐉 URL Info Gatherer v3.0 - 3 Başlı Ejderha                          ║
║   🔴 Red Team | 🟣 Purple Team | 🔵 Blue Team                          ║
║   🌐 WHOIS | DNS | SSL | Screenshot | Tech Detect | Subdomain         ║
╚══════════════════════════════════════════════════════════════════════════╝

📊 Tarama Bilgileri:
  • Hedef sayısı: 1
  • Screenshot: Aktif
  • Subdomain: Aktif

============================================================
[+] Analiz ediliyor: https://github.com
============================================================

📌 URL: https://github.com
✓ Status: 200
✓ Title: GitHub · Change is constant. GitHub keeps you ahead.
✓ Server: github.com
✓ Technologies: Shopify, React, Ruby on Rails
✓ Security Headers:
  ✅ Strict-Transport-Security
  ✅ Content-Security-Policy
  ✅ X-Frame-Options
✓ SSL: 2026-06-03 (50 gün kaldı)
✓ IP: 140.82.121.3
✓ Location: Frankfurt am Main, Germany
✓ Emails: you@domain.com
✓ Social Media: Twitter, Instagram, LinkedIn, GitHub
✓ Screenshot: screenshots/github.com_20260414_145038.png
✓ Subdomains Bulunan: 16

============================================================
```

---

## ⚠️ Uyarı

> Bu araç **eğitim ve yetkili testler** için geliştirilmiştir. İzinsiz kullanım yasa dışıdır. Sorumluluk kullanıcıya aittir.

---

## ⭐ Star Atmayı Unutma!

Beğendiysen GitHub'da ⭐ bırakmayı unutma!

---

## 📝 Sürüm Geçmişi

| Sürüm | Yenilikler |
|-------|------------|
| v3.0 | Screenshot, subdomain, email, sosyal medya, güvenlik başlıkları, 25+ teknoloji |
| v2.0 | DNS, WHOIS, SSL, teknoloji tespiti |
| v1.0 | Temel HTTP bilgileri |
```
Sıradaki araç hangisi? Dobivorn ekibinin diğer üyelerini de güncellemeye devam edelim mi? 
