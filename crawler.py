import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import threading
import time
import re
import tldextract
from bdd import BDD
from indexation import Indexation
from datetime import datetime, timedelta
import socket
from dotenv import load_dotenv
import os
import hashlib

class Crawler:
    def __init__(self, urls, request_delay=1):
        load_dotenv()
        self.indexation = Indexation()
        self.lock = threading.Lock()
        self.max_threads = int(os.getenv("MAX_THREADS"), 10)
        self.request_delay = request_delay
        self.user_agent = "FulgureBotSearch/1.0"
        self.last_visited = {}
        self.bdd = BDD()
        self.miniqueue = []
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
    
    def get_sitemap(self, url):
        pass

    def hash_content(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_content(self, soup):
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        text = soup.get_text(separator=" ", strip=True)

        # Nettoyer les espaces inutiles
        text = " ".join(text.split())

        return self.hash_content(text)
    
    def get_content_update(self, soup, url):
        if self.bdd.get_content(url) == self.get_content(soup):
            return False
        else:
            return True
        
    def get_priority_recrawl(page_data):
        min_priority = 1.0
        max_priority = 10.0

        # Récupération PageRank normalisé [0,1]
        pagerank = page_data.get("PageRank", 0)
        pagerank = max(0.0, min(pagerank, 1.0))

        # Récupération date dernière mise à jour
        content_update_at = page_data.get("content_update_at")
        if content_update_at:
            try:
                last_update = datetime.strptime(content_update_at, "%Y-%m-%d %H:%M:%S.%f")
                age = (datetime.now() - last_update).total_seconds()
            except Exception:
                age = 365 * 24 * 3600  # 1 an en secondes
        else:
            age = 365 * 24 * 3600  # 1 an

        # Normaliser l'âge sur une échelle (par exemple entre 0 sec et 30 jours)
        max_age_seconds = 30 * 24 * 3600  # 30 jours en secondes
        age_norm = min(age / max_age_seconds, 1.0)  # entre 0 et 1

        # Calcul d'un score combiné
        # On peut pondérer âge (70%) et pagerank (30%)
        combined_score = 0.7 * age_norm + 0.3 * pagerank  # valeur entre 0 et 1

        # Échelle vers 1 à 10
        priority = min_priority + combined_score * (max_priority - min_priority)

        return round(priority, 2)

    def recrawl_page(self, url):
        try:
            reponse = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=5)
            if(reponse.status_code != 200):
                return
            soup = BeautifulSoup(reponse.text, "html.parser")
            if not self.get_content_update(soup, url):
                return
            
            page_data = self.get_webpage(url)
            if not page_data:
                return
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

            
            page_data.update({
                "url": url,
                "title": title,
                "h1_tags": h1_tags,
                "h2_tags": h2_tags,
                "description": description,
                "keywords": keywords,
                "text": text,
                "link_to": all_valid_links,
                "PageRank": 1,
                "content": self.get_content(soup),
                "priority_crawled": self.get_priority_recrawl(page_data),
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "content_update_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            })
            self.bdd.update_webpage(page_data)
            self.indexation.add_number_of_words(url)
            self.indexation.inverted_index_in_text(url)
            self.indexation.inverted_index_in_titles(url)
            self.indexation.page_rank(url)

        except Exception as e:
            print(e)

    def crawl_page(self, url):
        try:
            #print("Je crawle ce site: ", url)
            if self.bdd.check_if_crawled(url):
                self.recrawl_page(url)
                return
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
                "content": self.get_content(soup),
                "priority_crawled": 5,
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "content_update_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            self.bdd.save_page(page_data)
            self.indexation.add_number_of_words(url)
            self.indexation.inverted_index_in_text(url)
            self.indexation.inverted_index_in_titles(url)
            self.indexation.page_rank(url)
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

crawler = Crawler(["https://www.lemonde.fr", "https://google.com", "https://ovh.com", "https://fulgure.fr"])
crawler.start()