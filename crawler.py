import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import threading
import time
import re
import tldextract
from bdd import BDD
from datetime import datetime
import socket

class Crawler:
    def __init__(self, urls, max_threads, request_delay=1):
        self.lock = threading.Lock()
        self.max_threads = max_threads
        self.request_delay = request_delay
        self.user_agent = "FulgureBotSearch/1.0"
        self.last_visited = {}
        self.bdd = BDD()
        self.miniqueue = self.bdd.get_all_miniqueue()
        #self.get_all_ex_last_visited()
        #self.crawled = []
        for url in urls:
            if not self.bdd.check_if_crawled(url):
                self.bdd.add_to_queue(url, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                if not self.bdd.get_last_visited(url, 0):
                    self.bdd.add_to_last_visited(url, 0)

    def fill_mini_queue(self):
        self.miniqueue = self.miniqueue + self.bdd.get_queue(5000)
    
    def can_fetch(self, url):
        try:
            base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
            rp = RobotFileParser()
            rp.set_url(base_url + "/robots.txt")
            rp.read()
            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            print(e)
            return False

    def crawl_page(self, url):
        try:
            print("Je crawle ce site: ", url)
            reponse = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=5)
            if(reponse.status_code != 200):
                return
            soup = BeautifulSoup(reponse.text, "html.parser")

            title = soup.find('title').text if soup.find('title') else ""
            h1_tags = [tag.text for tag in soup.find_all('h1')]
            h2_tags = [tag.text for tag in soup.find_all('h2')]
            description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else ""
            keywords = soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find('meta', attrs={'name': 'keywords'}) else ""
            text = soup.get_text()

            base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
            links = soup.find_all('a', href=True)
            all_valid_links = []
            for link in links:
                href = link.get('href')
                if href and not href.startswith('http') and href.startswith('/'):
                    href = urljoin(base_url, href)
                if href and href.startswith('http') and not href.endswith('.pdf'):
                    all_valid_links.append(href)
                    if not self.bdd.get_last_visited(href, 0):
                        self.bdd.add_to_last_visited(href, 0)
                    self.bdd.add_to_queue(href, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

            
            page_data =  {
                "url": url,
                "title": title,
                "h1_tags": h1_tags,
                "h2_tags": h2_tags,
                "description": description,
                "keywords": keywords,
                "text": text,
                "link_to": all_valid_links,
                "PageRank": 0,
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            }
            self.bdd.save_page(page_data)
        except Exception as e:
            print(e)
        
        # Fin de la logique principal du crawler

    def crawler(self):
        while True:
            with self.lock:
                if not self.miniqueue:
                    self.fill_mini_queue()
                    if not self.miniqueue:
                        break
                url = self.miniqueue.pop()
            try:
                self.crawl_page(url)
            except Exception as e:
                print(e)

    def  start(self):
        threads = []
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.crawler)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

crawler = Crawler(["https://www.lemonde.fr", "https://google.com", "https://ovh.com", "https://fulgure.fr"], 100)
crawler.start()