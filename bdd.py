from pymongo import MongoClient, ASCENDING, errors
from dotenv import load_dotenv
import os
import time

class BDD:
    def __init__(self):
        load_dotenv()
        # Connexion à MongoDB
        self.client = MongoClient(os.getenv("DATABASE_URL"))
        # Création d'une nouvelle base de données
        self.db = self.client['fulgure']
        # Création de webpages
        self.webpages = self.db['webpages']
        self.webpages.create_index([("url", ASCENDING)], unique=True)
        # Création de miniqueue
        self.miniqueue = self.db['miniqueue']
        self.miniqueue.create_index([("url", ASCENDING)], unique=True)
        # Création de queue
        self.queue = self.db['queue']
        self.queue.create_index([("url", ASCENDING)], unique=True)
        # Création de last_visited
        self.last_visited = self.db['last_visited']
        self.last_visited.create_index([("url", ASCENDING)], unique=True)
        # Création de crawled
        self.crawled = self.db['crawled']
        self.crawled.create_index([("url", ASCENDING)], unique=True)

    def add_to_queue(self, url, date):
        if not self.queue.find_one({"url": url}):
            self.queue.insert_one({"url": url})
        
    def add_to_miniqueue(self, url, date):
        self.miniqueue.insert_one({"url": url, "date": date})
        
    def add_to_last_visited(self, url, date):
        self.last_visited.insert_one({"url": url, "date": date})
    
    def add_to_crawled(self, url, date):
        self.crawled.insert_one({"url": url, "date": date})
        
    def check_if_crawled(self, url):
        return self.crawled.find_one({"url": url})
    
    def get_all_miniqueue(self):
        return [x["url"] for x in self.miniqueue.find()]
        
    def get_queue(self, limit):
        urls = [x["url"] for x in self.queue.find().limit(limit)]
        for url in urls:
            self.queue.delete_one({"url": url})
        return urls
    
    def get_last_visited(self, url, limit):
        return self.last_visited.find_one({"url": url})
    
    def save_page(self, page_data):
        self.webpages.insert_one(page_data)