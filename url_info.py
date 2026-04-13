#!/usr/bin/env python3
import requests
import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse

def get_url_info(url):
    print(f"\n[+] Analiz ediliyor: {url}\n")
    
    # URL'yi düzelt (http eklemezse)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # HTTP isteği
        response = requests.get(url, timeout=10, verify=True)
        print(f"[✓] HTTP Durum Kodu: {response.status_code}")
        
        # Sunucı tipi
        server = response.headers.get('Server', 'Bilinmiyor')
        print(f"[✓] Sunucı: {server}")
        
        # Sayfa başlığı
        title_start = response.text.find('<title>')
        title_end = response.text.find('</title>')
        if title_start != -1 and title_end != -1:
            title = response.text[title_start+7:title_end]
            print(f"[✓] Sayfa Başlığı: {title[:60]}")
        else:
            print("[✓] Sayfa Başlığı: Bulunamadı")
            
    except Exception as e:
        print(f"[✗] HTTP Hatası: {e}")
    
    # SSL bilgisi (HTTPS için)
    if url.startswith('https://'):
        try:
            hostname = urlparse(url).hostname
            context = ssl.create_default_context()
            with context.wrap_socket(socket.socket(), server_hostname=hostname) as sock:
                sock.settimeout(10)
                sock.connect((hostname, 443))
                cert = sock.getpeercert()
                expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                print(f"[✓] SSL Bitiş: {expire_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"[✗] SSL Hatası: {e}")
    
    # IP adresi
    try:
        domain = urlparse(url).hostname
        ip = socket.gethostbyname(domain)
        print(f"[✓] IP Adresi: {ip}")
    except:
        print("[✗] IP Adresi alınamadı")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Kullanım: python url_info.py <url>")
        print("Örnek: python url_info.py https://google.com")
        sys.exit(1)
    
    get_url_info(sys.argv[1])
