#!/usr/bin/env python3
"""
URL Info Gatherer v2.0 🐉
3 Başlı Ejderha | Red Team | Purple Team | Blue Team

Özellikler:
- HTTP/HTTPS bilgileri (status, headers, title)
- SSL sertifika detayları
- DNS kayıtları (A, MX, TXT, NS, CNAME)
- WHOIS sorgulama
- Teknoloji tespiti
- Screenshot alma
- Çoklu URL desteği
- JSON/CSV raporlama
"""

import requests
import ssl
import socket
import dns.resolver
import whois
import json
import csv
import sys
import argparse
from datetime import datetime
from urllib.parse import urlparse
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# Uyarıları kapat
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Renkleri başlat
init(autoreset=True)

# Banner
BANNER = f"""
{Fore.BLUE}╔══════════════════════════════════════════════════════════════╗
║   🐉 URL Info Gatherer v2.0 - 3 Başlı Ejderha                ║
║   🔴 Red Team | 🟣 Purple Team | 🔵 Blue Team                ║
║   🌐 WHOIS | DNS | SSL | Screenshot | Tech Detect           ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# Teknoloji tespiti için imzalar
TECH_SIGNATURES = {
    'WordPress': ['wp-content', 'wp-includes', 'wp-json'],
    'Laravel': ['laravel_session', 'csrf-token'],
    'Django': ['csrftoken', 'admin/login'],
    'React': ['_next', 'react', 'manifest.json'],
    'Angular': ['_ng', 'ng-app'],
    'Bootstrap': ['bootstrap.min.css', 'bootstrap.js'],
    'jQuery': ['jquery.min.js', 'jquery.js'],
}

class URLInfoGatherer:
    def __init__(self, urls, output=None, format='json', screenshot=False, threads=5):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.output = output
        self.format = format
        self.screenshot = screenshot
        self.threads = threads
        self.results = []
        
    def normalize_url(self, url):
        """URL'yi düzelt"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def get_http_info(self, url):
        """HTTP bilgilerini topla"""
        info = {}
        try:
            response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
            info['status_code'] = response.status_code
            info['final_url'] = response.url
            info['content_length'] = len(response.content)
            info['server'] = response.headers.get('Server', 'Bilinmiyor')
            
            # Sayfa başlığı
            title_start = response.text.find('<title>')
            title_end = response.text.find('</title>')
            if title_start != -1 and title_end != -1:
                info['title'] = response.text[title_start+7:title_end][:100]
            else:
                info['title'] = 'Bulunamadı'
            
            # Teknoloji tespiti
            info['technologies'] = self.detect_technologies(response.text, response.headers)
            
            # Link bulma
            info['links'] = self.extract_links(response.text, url)
            
        except requests.exceptions.RequestException as e:
            info['error'] = str(e)
            info['status_code'] = 'Hata'
        
        return info
    
    def detect_technologies(self, html, headers):
        """Teknoloji tespiti yap"""
        detected = set()
        combined = html.lower() + str(headers).lower()
        
        for tech, indicators in TECH_SIGNATURES.items():
            for indicator in indicators:
                if indicator.lower() in combined:
                    detected.add(tech)
                    break
        
        # Server header'dan tespit
        if 'Server' in headers:
            server = headers['Server'].lower()
            if 'nginx' in server:
                detected.add('Nginx')
            elif 'apache' in server:
                detected.add('Apache')
            elif 'cloudflare' in server:
                detected.add('CloudFlare')
        
        return list(detected)
    
    def extract_links(self, html, base_url):
        """Sayfadaki linkleri bul"""
        links = set()
        pattern = r'href=["\'](https?://[^"\']+)["\']'
        matches = re.findall(pattern, html)
        for match in matches[:20]:
            links.add(match)
        return list(links)
    
    def get_ssl_info(self, domain):
        """SSL sertifika bilgileri"""
        info = {}
        try:
            context = ssl.create_default_context()
            with context.wrap_socket(socket.socket(), server_hostname=domain) as sock:
                sock.settimeout(10)
                sock.connect((domain, 443))
                cert = sock.getpeercert()
                
                not_after = cert.get('notAfter', '')
                if not_after:
                    expire_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    info['expires'] = expire_date.strftime('%Y-%m-%d')
                    info['days_left'] = (expire_date - datetime.now()).days
                else:
                    info['expires'] = 'Bilinmiyor'
                    info['days_left'] = '?'
                
                info['issuer'] = str(cert.get('issuer', 'Bilinmiyor'))
                
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def get_dns_info(self, domain):
        """DNS kayıtlarını sorgula"""
        info = {}
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
        
        for record in record_types:
            try:
                answers = dns.resolver.resolve(domain, record)
                info[record] = [str(answer) for answer in answers]
            except:
                info[record] = []
        
        return info
    
    def get_whois_info(self, domain):
        """WHOIS bilgileri"""
        try:
            w = whois.whois(domain)
            return {
                'registrar': str(w.registrar) if w.registrar else 'Bilinmiyor',
                'creation_date': str(w.creation_date) if w.creation_date else 'Bilinmiyor',
                'expiration_date': str(w.expiration_date) if w.expiration_date else 'Bilinmiyor',
                'name_servers': w.name_servers if w.name_servers else [],
                'org': str(w.org) if w.org else 'Bilinmiyor',
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_ip_info(self, domain):
        """IP adresi ve lokasyon bilgisi"""
        info = {}
        try:
            ip = socket.gethostbyname(domain)
            info['ip'] = ip
            
            # IP lokasyon
            try:
                response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        info['country'] = data.get('country', 'Bilinmiyor')
                        info['city'] = data.get('city', 'Bilinmiyor')
                        info['isp'] = data.get('isp', 'Bilinmiyor')
            except:
                pass
                
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def take_screenshot(self, url):
        """Screenshot URL'si oluştur"""
        return {'screenshot_url': f"https://api.microlink.io?url={url}&screenshot=true"}
    
    def analyze_url(self, url):
        """Tüm bilgileri topla"""
        print(f"\n{Fore.CYAN}[+] Analiz ediliyor: {url}{Style.RESET_ALL}")
        
        normalized_url = self.normalize_url(url)
        parsed = urlparse(normalized_url)
        domain = parsed.hostname
        
        result = {
            'url': url,
            'timestamp': str(datetime.now()),
            'http': self.get_http_info(normalized_url),
            'ip': self.get_ip_info(domain),
            'dns': self.get_dns_info(domain),
        }
        
        # SSL sadece HTTPS için
        if parsed.scheme == 'https':
            result['ssl'] = self.get_ssl_info(domain)
        
        # WHOIS
        result['whois'] = self.get_whois_info(domain)
        
        # Screenshot
        if self.screenshot:
            result['screenshot'] = self.take_screenshot(normalized_url)
        
        # Konsola yazdır
        self.print_result(result)
        
        return result
    
    def print_result(self, result):
        """Sonuçları konsola yazdır"""
        url = result['url']
        http = result['http']
        
        print(f"{Fore.GREEN}[✓] URL: {url}{Style.RESET_ALL}")
        
        if 'error' in http:
            print(f"{Fore.RED}[✗] Hata: {http['error']}{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}[✓] Status: {http.get('status_code', '?')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Title: {http.get('title', '?')[:50]}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Server: {http.get('server', '?')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Content Length: {http.get('content_length', '?')} bytes{Style.RESET_ALL}")
        
        if http.get('technologies'):
            print(f"{Fore.MAGENTA}[✓] Technologies: {', '.join(http['technologies'])}{Style.RESET_ALL}")
        
        # SSL
        if 'ssl' in result and result['ssl'].get('expires'):
            ssl_info = result['ssl']
            print(f"{Fore.GREEN}[✓] SSL Expires: {ssl_info['expires']} ({ssl_info.get('days_left', '?')} days left){Style.RESET_ALL}")
        
        # IP
        ip_info = result['ip']
        if 'ip' in ip_info:
            print(f"{Fore.GREEN}[✓] IP: {ip_info['ip']}{Style.RESET_ALL}")
            if 'country' in ip_info:
                print(f"{Fore.GREEN}[✓] Location: {ip_info.get('city', '')}, {ip_info['country']}{Style.RESET_ALL}")
            if 'isp' in ip_info:
                print(f"{Fore.GREEN}[✓] ISP: {ip_info['isp']}{Style.RESET_ALL}")
        
        # DNS
        dns = result['dns']
        if dns.get('A'):
            print(f"{Fore.CYAN}[✓] DNS A: {', '.join(dns['A'][:3])}{Style.RESET_ALL}")
        if dns.get('MX'):
            print(f"{Fore.CYAN}[✓] DNS MX: {', '.join(dns['MX'][:2])}{Style.RESET_ALL}")
        
        # Links
        if http.get('links'):
            print(f"{Fore.CYAN}[✓] Links found: {len(http['links'])}{Style.RESET_ALL}")
    
    def scan_all(self):
        """Tüm URL'leri tara"""
        print(BANNER)
        print(f"{Fore.YELLOW}[+] Hedef sayısı: {len(self.urls)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[+] Thread: {self.threads}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[+] Screenshot: {'Aktif' if self.screenshot else 'Kapalı'}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[+] Başlangıç: {datetime.now()}{Style.RESET_ALL}")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.analyze_url, url): url for url in self.urls}
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
        
        self.generate_report()
    
    def generate_report(self):
        """Rapor oluştur"""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║                    RAPOR ÖZETİ                                      ║")
        print(f"╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[+] Toplam URL: {len(self.results)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[+] Bitiş: {datetime.now()}{Style.RESET_ALL}")
        
        if self.output:
            if self.format == 'json':
                with open(self.output, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
                print(f"{Fore.GREEN}[+] JSON raporu kaydedildi: {self.output}{Style.RESET_ALL}")
            elif self.format == 'csv':
                with open(self.output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['url', 'status', 'title', 'server', 'ip', 'technologies'])
                    writer.writeheader()
                    for r in self.results:
                        writer.writerow({
                            'url': r['url'],
                            'status': r['http'].get('status_code', ''),
                            'title': r['http'].get('title', ''),
                            'server': r['http'].get('server', ''),
                            'ip': r['ip'].get('ip', ''),
                            'technologies': ', '.join(r['http'].get('technologies', []))
                        })
                print(f"{Fore.GREEN}[+] CSV raporu kaydedildi: {self.output}{Style.RESET_ALL}")

def load_urls_from_file(file_path):
    """Dosyadan URL listesi oku"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(
        description="URL Info Gatherer v2.0 - URL Bilgi Toplama Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python url_info.py https://google.com
  python url_info.py -f urls.txt -t 10
  python url_info.py https://google.com -o sonuc.json
  python url_info.py https://google.com --screenshot
        """
    )
    
    parser.add_argument("url", nargs='?', help="Hedef URL")
    parser.add_argument("-f", "--file", help="URL listesi içeren dosya")
    parser.add_argument("-o", "--output", help="Çıktı dosyası")
    parser.add_argument("--format", choices=['json', 'csv'], default='json', help="Çıktı formatı")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Thread sayısı")
    parser.add_argument("--screenshot", action="store_true", help="Screenshot URL'si ekle")
    
    args = parser.parse_args()
    
    # URL'leri topla
    urls = []
    if args.url:
        urls.append(args.url)
    if args.file:
        try:
            urls.extend(load_urls_from_file(args.file))
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Dosya bulunamadı: {args.file}{Style.RESET_ALL}")
            sys.exit(1)
    
    if not urls:
        print(f"{Fore.RED}[!] En az bir URL belirtin!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Kullanım: python url_info.py https://google.com{Style.RESET_ALL}")
        sys.exit(1)
    
    # Tarama başlat
    gatherer = URLInfoGatherer(urls, args.output, args.format, args.screenshot, args.threads)
    gatherer.scan_all()

if __name__ == "__main__":
    main()
