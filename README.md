# URL Info Gatherer

🐉 **Dobivorn** tarafından geliştirilen basit bir URL bilgi toplama aracı.

## Özellikler

- HTTP durum kodu
- Sunucu tipi (Server header)
- Sayfa başlığı
- SSL sertifikası bitiş tarihi
- IP adresi

## Kurulum

git clone https://github.com/DobivornSec/url-info-gatherer.git
cd url-info-gatherer
pip install -r requirements.txt

## Kullanım

python url_info.py https://example.com

# Örnek Çıktı

[+] Analiz ediliyor: https://google.com

[✓] HTTP Durum Kodu: 200
[✓] Sunucu: gws
[✓] Sayfa Başlığı: Google
[✓] SSL Bitiş: 2025-12-01
[✓] IP Adresi: 142.250.185.46
