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
        self.get_all_ex_last_visited()
        #self.crawled = []
        for url in urls:
            if not self.bdd.check_if_crawled(url):
                self.bdd.add_to_queue(url, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                if not self.get_last_visited(url, 0):
                    self.add_to_last_visited(url, 0)

    def fill_mini_queue(self):
        self.miniqueue = self.miniqueue + self.bdd.get_queue(5000)

    def crawler(self):
        while True:
            pass

    def  start(self):
        threads = []
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.crawler)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()