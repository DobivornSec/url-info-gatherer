#!/usr/bin/env python3
"""
URL Info Gatherer v3.0 🐉
3 Başlı Ejderha | Red Team | Purple Team | Blue Team

v3.0 Yenilikler:
- Screenshot gerçek görüntü kaydetme (webdriver-manager ile)
- Subdomain bulma (DNS brute force)
- Email scraping
- Sosyal medya bağlantıları tespiti
- Gelişmiş teknoloji tespiti (25+)
- Güvenlik başlıkları analizi
- Daha hızlı thread yönetimi
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
import os
import re
import subprocess
from datetime import datetime
from urllib.parse import urlparse
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed

# Screenshot için (opsiyonel - hata yönetimi eklendi)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import time

# Uyarıları kapat
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Renkleri başlat
init(autoreset=True)

# Banner
BANNER = f"""
{Fore.BLUE}╔══════════════════════════════════════════════════════════════════════════╗
║   🐉 URL Info Gatherer v3.0 - 3 Başlı Ejderha                          ║
║   🔴 Red Team | 🟣 Purple Team | 🔵 Blue Team                          ║
║   🌐 WHOIS | DNS | SSL | Screenshot | Tech Detect | Subdomain         ║
╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# Gelişmiş teknoloji tespiti imzaları
TECH_SIGNATURES = {
    'CMS': {
        'WordPress': ['wp-content', 'wp-includes', 'wp-json', 'wordpress'],
        'Joomla': ['joomla', 'com_content', 'com_users'],
        'Drupal': ['drupal', 'sites/default', 'core/misc'],
        'Magento': ['magento', 'skin/frontend'],
        'Shopify': ['shopify', 'myshopify.com'],
        'Wix': ['wix.com', 'wixstatic'],
    },
    'Framework': {
        'Laravel': ['laravel_session', 'csrf-token', 'laravel'],
        'Django': ['csrftoken', 'admin/login', 'django'],
        'React': ['_next', 'react', 'manifest.json', 'react-dom'],
        'Angular': ['_ng', 'ng-app', 'angular'],
        'Vue.js': ['vue.js', 'vue.min', 'data-v-'],
        'Flask': ['flask', '__debug__'],
        'Express': ['express', 'x-powered-by: express'],
        'Ruby on Rails': ['rails', 'csrf-param', 'authenticity_token'],
    },
    'Library': {
        'jQuery': ['jquery.min.js', 'jquery.js', 'jquery-'],
        'Bootstrap': ['bootstrap.min.css', 'bootstrap.css', 'bootstrap.js'],
        'Tailwind': ['tailwind.css', 'tailwind.min'],
        'FontAwesome': ['fontawesome', 'fa.min.css'],
        'Google Fonts': ['fonts.googleapis.com'],
    },
    'Analytics': {
        'Google Analytics': ['google-analytics.com', 'ga.js', 'gtag'],
        'Facebook Pixel': ['facebook.com/tr', 'fbq'],
    },
    'CDN': {
        'CloudFlare': ['cloudflare', 'cf-ray', '__cfduid'],
        'Akamai': ['akamai', 'akamaiedge'],
        'Fastly': ['fastly', 'x-fastly'],
    }
}

# Sosyal medya pattern'leri
SOCIAL_PATTERNS = {
    'Twitter': r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)',
    'Instagram': r'instagram\.com/([a-zA-Z0-9_.]+)',
    'Facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
    'LinkedIn': r'linkedin\.com/(?:company|in)/([a-zA-Z0-9-]+)',
    'GitHub': r'github\.com/([a-zA-Z0-9-]+)',
    'YouTube': r'youtube\.com/(?:c|channel|user)/([a-zA-Z0-9_-]+)',
    'Discord': r'discord\.(?:gg|com/invite)/([a-zA-Z0-9]+)',
    'Telegram': r't\.me/([a-zA-Z0-9_]+)',
}

# Ortak subdomain listesi
COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
    'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'blog', 'shop', 'store',
    'support', 'dev', 'test', 'stage', 'api', 'app', 'admin', 'login', 'account',
    'secure', 'vpn', 'remote', 'wiki', 'docs', 'static', 'media', 'cdn', 'img',
    'video', 'download', 'backup', 'dns', 'mail2', 'forum', 'community',
    'news', 'portal', 'partner', 'status', 'demo', 'beta', 'sandbox'
]

class URLInfoGathererV3:
    def __init__(self, urls, output=None, format='json', screenshot=False, threads=5, subdomain=False):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.output = output
        self.format = format
        self.screenshot = screenshot
        self.threads = threads
        self.subdomain = subdomain
        self.results = []
        self.screenshot_dir = "screenshots"
        
        if screenshot:
            os.makedirs(self.screenshot_dir, exist_ok=True)
            if not SELENIUM_AVAILABLE:
                print(f"{Fore.YELLOW}[!] Uyarı: Selenium kurulu değil. Screenshot özelliği çalışmayacak.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    Kurulum için: pip install selenium webdriver-manager{Style.RESET_ALL}")
        
    def normalize_url(self, url):
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def get_http_info(self, url):
        info = {
            'status_code': 'Hata',
            'final_url': url,
            'content_length': 0,
            'server': 'Bilinmiyor',
            'title': 'Bulunamadı',
            'technologies': [],
            'links': [],
            'emails': [],
            'social_media': [],
            'security_headers': {}
        }
        
        try:
            response = requests.get(url, timeout=15, verify=False, allow_redirects=True)
            info['status_code'] = response.status_code
            info['final_url'] = response.url
            info['content_length'] = len(response.content)
            info['server'] = response.headers.get('Server', 'Bilinmiyor')
            info['security_headers'] = self.check_security_headers(response.headers)
            
            # Title
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            if title_match:
                info['title'] = title_match.group(1).strip()[:150]
            
            # Teknoloji tespiti
            info['technologies'] = self.detect_technologies(response.text, response.headers)
            
            # Linkler
            info['links'] = self.extract_links(response.text, url)
            
            # Email scraping
            info['emails'] = self.extract_emails(response.text)
            
            # Sosyal medya
            info['social_media'] = self.extract_social_media(response.text)
            
        except requests.exceptions.Timeout:
            info['error'] = 'Timeout'
        except requests.exceptions.ConnectionError:
            info['error'] = 'Connection Error'
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def check_security_headers(self, headers):
        security_headers = {
            'Strict-Transport-Security': '❌',
            'Content-Security-Policy': '❌',
            'X-Frame-Options': '❌',
            'X-Content-Type-Options': '❌',
            'Referrer-Policy': '❌',
            'Permissions-Policy': '❌'
        }
        
        for header in security_headers.keys():
            if header in headers:
                security_headers[header] = '✅'
        
        return security_headers
    
    def detect_technologies(self, html, headers):
        detected = []
        combined = html.lower()
        
        for category, techs in TECH_SIGNATURES.items():
            for tech, indicators in techs.items():
                for indicator in indicators:
                    if indicator.lower() in combined:
                        detected.append(tech)
                        break
        
        # Server header kontrolü
        if 'Server' in headers:
            server = headers['Server'].lower()
            if 'nginx' in server:
                detected.append('Nginx')
            elif 'apache' in server:
                detected.append('Apache')
            elif 'cloudflare' in server:
                detected.append('CloudFlare')
            elif 'iis' in server:
                detected.append('IIS')
        
        return list(dict.fromkeys(detected))
    
    def extract_links(self, html, base_url):
        links = set()
        patterns = [
            r'href=["\'](https?://[^"\']+)["\']',
            r'src=["\'](https?://[^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches[:30]:
                links.add(match)
        
        return list(links)
    
    def extract_emails(self, html):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, html)
        return list(dict.fromkeys(emails[:20]))
    
    def extract_social_media(self, html):
        found = []
        for platform, pattern in SOCIAL_PATTERNS.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                found.append({
                    'platform': platform,
                    'handle': match,
                    'url': f"https://{platform.lower()}.com/{match}" if platform != 'Twitter' else f"https://twitter.com/{match}"
                })
        return found[:15]
    
    def get_ssl_info(self, domain):
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
                info['subject'] = str(cert.get('subject', 'Bilinmiyor'))
                info['valid'] = info.get('days_left', 0) > 0 if info.get('days_left') != '?' else False
                
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def get_dns_info(self, domain):
        info = {}
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
        
        for record in record_types:
            try:
                answers = dns.resolver.resolve(domain, record)
                info[record] = [str(answer) for answer in answers]
            except:
                info[record] = []
        
        return info
    
    def get_whois_info(self, domain):
        try:
            w = whois.whois(domain)
            return {
                'registrar': str(w.registrar) if w.registrar else 'Bilinmiyor',
                'creation_date': str(w.creation_date) if w.creation_date else 'Bilinmiyor',
                'expiration_date': str(w.expiration_date) if w.expiration_date else 'Bilinmiyor',
                'updated_date': str(w.updated_date) if w.updated_date else 'Bilinmiyor',
                'name_servers': w.name_servers if w.name_servers else [],
                'org': str(w.org) if w.org else 'Bilinmiyor',
                'country': str(w.country) if w.country else 'Bilinmiyor',
                'emails': w.emails if hasattr(w, 'emails') else []
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_ip_info(self, domain):
        info = {}
        try:
            ip = socket.gethostbyname(domain)
            info['ip'] = ip
            
            try:
                response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        info['country'] = data.get('country', 'Bilinmiyor')
                        info['city'] = data.get('city', 'Bilinmiyor')
                        info['region'] = data.get('regionName', 'Bilinmiyor')
                        info['isp'] = data.get('isp', 'Bilinmiyor')
                        info['org'] = data.get('org', 'Bilinmiyor')
                        info['timezone'] = data.get('timezone', 'Bilinmiyor')
            except:
                pass
                
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def find_subdomains(self, domain):
        """Subdomain bulma (DNS brute force)"""
        found = []
        print(f"\n{Fore.YELLOW}[*] Subdomain aranıyor: {domain}{Style.RESET_ALL}")
        
        for sub in COMMON_SUBDOMAINS:
            test_domain = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(test_domain)
                found.append({
                    'subdomain': test_domain,
                    'ip': ip,
                    'alive': True
                })
                print(f"{Fore.GREEN}[+] Bulundu: {test_domain} -> {ip}{Style.RESET_ALL}")
            except:
                pass
        
        return found
    
    def take_screenshot(self, url, domain):
        """Gerçek screenshot al - webdriver-manager ile"""
        if not self.screenshot:
            return None
        
        if not SELENIUM_AVAILABLE:
            return "Hata: Selenium kurulu değil. 'pip install selenium webdriver-manager'"
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            
            # Chromium binary yolunu zorla belirt
            chrome_options.binary_location = "/usr/bin/chromium"
            
            # Önce sistemdeki chromedriver'ı kontrol et
            result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
            system_chromedriver = result.stdout.strip()
            
            if system_chromedriver and os.path.exists(system_chromedriver):
                # Sistem chromedriver'ını kullan
                service = Service(system_chromedriver)
                print(f"{Fore.CYAN}[*] Sistem chromedriver'ı kullanılıyor: {system_chromedriver}{Style.RESET_ALL}")
            else:
                # Yoksa webdriver-manager'ı kullan
                service = Service(ChromeDriverManager().install())
                print(f"{Fore.CYAN}[*] webdriver-manager ile chromedriver indiriliyor...{Style.RESET_ALL}")
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            time.sleep(3)
            
            filename = f"{self.screenshot_dir}/{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(filename)
            driver.quit()
            
            return filename
        except Exception as e:
            return f"Hata: {str(e)[:200]}"
    
    def analyze_url(self, url):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"[+] Analiz ediliyor: {url}")
        print(f"{'='*60}{Style.RESET_ALL}")
        
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
        
        # SSL
        if parsed.scheme == 'https':
            result['ssl'] = self.get_ssl_info(domain)
        
        # WHOIS
        result['whois'] = self.get_whois_info(domain)
        
        # Screenshot
        if self.screenshot:
            screenshot_path = self.take_screenshot(normalized_url, domain)
            result['screenshot_path'] = screenshot_path
        
        # Subdomain
        if self.subdomain:
            result['subdomains'] = self.find_subdomains(domain)
        
        self.print_result(result)
        return result
    
    def print_result(self, result):
        url = result['url']
        http = result['http']
        
        print(f"\n{Fore.GREEN}📌 URL: {url}{Style.RESET_ALL}")
        
        if 'error' in http and http['error'] != 'Hata':
            print(f"{Fore.RED}✗ Hata: {http['error']}{Style.RESET_ALL}")
            return
        
        # Status
        status = http.get('status_code', '?')
        if status == 200:
            print(f"{Fore.GREEN}✓ Status: {status}{Style.RESET_ALL}")
        elif status in [301, 302, 307, 308]:
            print(f"{Fore.YELLOW}✓ Status: {status} (Redirect){Style.RESET_ALL}")
        elif status in [403, 404, 500, 502, 503]:
            print(f"{Fore.RED}✓ Status: {status}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}✓ Status: {status}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✓ Title: {http.get('title', '?')[:80]}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Server: {http.get('server', '?')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Content Length: {http.get('content_length', '?')} bytes{Style.RESET_ALL}")
        
        # Technologies
        if http.get('technologies'):
            tech_str = ', '.join(http['technologies'][:10])
            print(f"{Fore.MAGENTA}✓ Technologies: {tech_str}{Style.RESET_ALL}")
        
        # Security Headers
        if http.get('security_headers'):
            print(f"{Fore.CYAN}✓ Security Headers:{Style.RESET_ALL}")
            for header, status in http['security_headers'].items():
                color = Fore.GREEN if status == '✅' else Fore.RED
                print(f"  {color}{status} {header}{Style.RESET_ALL}")
        
        # SSL
        if 'ssl' in result and result['ssl'].get('expires'):
            ssl = result['ssl']
            if ssl.get('valid', False):
                print(f"{Fore.GREEN}✓ SSL: {ssl['expires']} ({ssl.get('days_left', '?')} gün kaldı){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✓ SSL: SÜRESİ DOLDU!{Style.RESET_ALL}")
        
        # IP
        ip = result['ip']
        if 'ip' in ip:
            print(f"{Fore.GREEN}✓ IP: {ip['ip']}{Style.RESET_ALL}")
            if 'country' in ip:
                print(f"{Fore.GREEN}✓ Location: {ip.get('city', '')}, {ip['country']}{Style.RESET_ALL}")
            if 'isp' in ip:
                print(f"{Fore.GREEN}✓ ISP: {ip['isp']}{Style.RESET_ALL}")
        
        # Emails
        if http.get('emails'):
            print(f"{Fore.YELLOW}✓ Emails: {', '.join(http['emails'][:5])}{Style.RESET_ALL}")
        
        # Social Media
        if http.get('social_media'):
            print(f"{Fore.MAGENTA}✓ Social Media:{Style.RESET_ALL}")
            for sm in http['social_media'][:5]:
                print(f"  {Fore.CYAN}→ {sm['platform']}: {sm['handle']}{Style.RESET_ALL}")
        
        # Screenshot
        if 'screenshot_path' in result and result['screenshot_path']:
            if not result['screenshot_path'].startswith('Hata'):
                print(f"{Fore.GREEN}✓ Screenshot: {result['screenshot_path']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✓ Screenshot: {result['screenshot_path'][:100]}{Style.RESET_ALL}")
        
        # Subdomains
        if 'subdomains' in result and result['subdomains']:
            print(f"{Fore.CYAN}✓ Subdomains Bulunan: {len(result['subdomains'])}{Style.RESET_ALL}")
            for sub in result['subdomains'][:10]:
                print(f"  → {sub['subdomain']} ({sub['ip']})")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def scan_all(self):
        print(BANNER)
        print(f"{Fore.YELLOW}📊 Tarama Bilgileri:{Style.RESET_ALL}")
        print(f"  • Hedef sayısı: {len(self.urls)}")
        print(f"  • Thread sayısı: {self.threads}")
        print(f"  • Screenshot: {'Aktif' if self.screenshot else 'Kapalı'}")
        print(f"  • Subdomain: {'Aktif' if self.subdomain else 'Kapalı'}")
        print(f"  • Başlangıç: {datetime.now()}\n")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.analyze_url, url): url for url in self.urls}
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
        
        self.generate_report()
    
    def generate_report(self):
        print(f"\n{Fore.BLUE}╔══════════════════════════════════════════════════════════════════════════╗")
        print(f"║                         RAPOR ÖZETİ                                              ║")
        print(f"╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}✓ Toplam URL: {len(self.results)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}✓ Bitiş: {datetime.now()}{Style.RESET_ALL}")
        
        total_emails = sum(len(r['http'].get('emails', [])) for r in self.results)
        total_links = sum(len(r['http'].get('links', [])) for r in self.results)
        total_techs = sum(len(r['http'].get('technologies', [])) for r in self.results)
        
        print(f"{Fore.CYAN}✓ Toplam email: {total_emails}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}✓ Toplam link: {total_links}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}✓ Toplam teknoloji: {total_techs}{Style.RESET_ALL}")
        
        if self.output:
            if self.format == 'json':
                with open(self.output, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
                print(f"{Fore.GREEN}✓ JSON raporu: {self.output}{Style.RESET_ALL}")
            elif self.format == 'csv':
                with open(self.output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['url', 'status', 'title', 'server', 'ip', 'technologies', 'emails'])
                    writer.writeheader()
                    for r in self.results:
                        writer.writerow({
                            'url': r['url'],
                            'status': r['http'].get('status_code', ''),
                            'title': r['http'].get('title', ''),
                            'server': r['http'].get('server', ''),
                            'ip': r['ip'].get('ip', ''),
                            'technologies': ', '.join(r['http'].get('technologies', [])),
                            'emails': ', '.join(r['http'].get('emails', []))
                        })
                print(f"{Fore.GREEN}✓ CSV raporu: {self.output}{Style.RESET_ALL}")

def load_urls_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(
        description="URL Info Gatherer v3.0 - URL Bilgi Toplama Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python url_info.py https://google.com
  python url_info.py -f urls.txt -t 10
  python url_info.py https://google.com -o rapor.json
  python url_info.py https://google.com --screenshot
  python url_info.py https://google.com --subdomain
  python url_info.py https://google.com -o rapor.csv --format csv
        """
    )
    
    parser.add_argument("url", nargs='?', help="Hedef URL")
    parser.add_argument("-f", "--file", help="URL listesi içeren dosya")
    parser.add_argument("-o", "--output", help="Çıktı dosyası")
    parser.add_argument("--format", choices=['json', 'csv'], default='json', help="Çıktı formatı")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Thread sayısı (varsayılan: 5)")
    parser.add_argument("--screenshot", action="store_true", help="Screenshot al")
    parser.add_argument("--subdomain", action="store_true", help="Subdomain ara")
    
    args = parser.parse_args()
    
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
    
    gatherer = URLInfoGathererV3(urls, args.output, args.format, args.screenshot, args.threads, args.subdomain)
    gatherer.scan_all()

if __name__ == "__main__":
    main()
