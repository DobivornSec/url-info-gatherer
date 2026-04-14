# 🐉 URL Info Gatherer v2.0

> **3 Başlı Ejderha** | Red Team | Purple Team | Blue Team

Web siteleri hakkında **kapsamlı bilgi** toplama aracı. HTTP, SSL, DNS, WHOIS, teknoloji tespiti ve daha fazlası.

---

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🌐 **HTTP Bilgileri** | Status kod, sunucu, başlık, içerik uzunluğu |
| 🔒 **SSL Sertifika** | Bitiş tarihi, kalan gün, issuer bilgisi |
| 📡 **DNS Kayıtları** | A, AAAA, MX, TXT, NS, CNAME |
| 📋 **WHOIS Sorgulama** | Domain kayıt bilgileri, son kullanma tarihi |
| 🕵️ **Teknoloji Tespiti** | WordPress, Laravel, React, Angular, Django |
| 📸 **Screenshot** | Site görseli URL'si (opsiyonel) |
| 🔗 **Link Bulma** | Sayfadaki tüm linkleri çıkarma |
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
pip install requests dnspython python-whois colorama
```

---

## 🚀 Kullanım

### Tek URL analizi
```bash
python url_info.py https://google.com
```

### Çoklu URL (dosyadan)
```bash
# urls.txt dosyası oluştur
echo "https://google.com" > urls.txt
echo "https://github.com" >> urls.txt

# Tüm URL'leri tara
python url_info.py -f urls.txt -t 10
```

### JSON rapor kaydetme
```bash
python url_info.py https://google.com -o rapor.json
```

### CSV rapor kaydetme
```bash
python url_info.py https://google.com -o rapor.csv --format csv
```

### Screenshot URL'si ile
```bash
python url_info.py https://google.com --screenshot
```

---

## 📊 Örnek Çıktı

```bash
╔══════════════════════════════════════════════════════════════╗
║   🐉 URL Info Gatherer v2.0 - 3 Başlı Ejderha                ║
║   🔴 Red Team | 🟣 Purple Team | 🔵 Blue Team                ║
║   🌐 WHOIS | DNS | SSL | Screenshot | Tech Detect           ║
╚══════════════════════════════════════════════════════════════╝

[+] Analiz ediliyor: https://google.com

[✓] URL: https://google.com
[✓] Status: 200
[✓] Title: Google
[✓] Server: gws
[✓] Content Length: 79832 bytes
[✓] SSL Expires: 2026-06-15 (61 days left)
[✓] IP: 172.217.16.142
[✓] Location: Frankfurt am Main, Germany
[✓] ISP: Google LLC
[✓] DNS A: 172.217.16.142
[✓] DNS MX: 10 smtp.google.com.
[✓] Links found: 6

╔══════════════════════════════════════════════════════════════╗
║                    RAPOR ÖZETİ                              ║
╚══════════════════════════════════════════════════════════════╝
[+] Toplam URL: 1
[+] Bitiş: 2026-04-14 12:13:03
[+] JSON raporu kaydedildi: rapor.json
```

---

## 🔧 Parametreler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `url` | Hedef URL | Zorunlu |
| `-f, --file` | URL listesi dosyası | Yok |
| `-o, --output` | Çıktı dosyası | Yok |
| `--format` | JSON veya CSV | `json` |
| `-t, --threads` | Thread sayısı | 5 |
| `--screenshot` | Screenshot URL'si ekle | Kapalı |

---

## 📁 Örnek JSON Rapor

```json
{
  "url": "https://google.com",
  "timestamp": "2026-04-14 12:13:14",
  "http": {
    "status_code": 200,
    "server": "gws",
    "title": "Google",
    "content_length": 79785
  },
  "ssl": {
    "expires": "2026-06-15",
    "days_left": 61
  },
  "ip": {
    "ip": "172.217.16.142",
    "country": "Germany",
    "isp": "Google LLC"
  },
  "dns": {
    "A": ["172.217.16.142"],
    "MX": ["10 smtp.google.com."]
  },
  "whois": {
    "registrar": "MarkMonitor, Inc.",
    "creation_date": "1997-09-15",
    "expiration_date": "2028-09-14"
  }
}
```

---

## ⚠️ Uyarı

> Bu araç **eğitim ve yetkili testler** için geliştirilmiştir. İzinsiz kullanım yasa dışıdır. Sorumluluk kullanıcıya aittir.

## ⭐ Star Atmayı Unutma!

Beğendiysen GitHub'da ⭐ bırakmayı unutma!
