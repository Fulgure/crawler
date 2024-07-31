from pymongo import MongoClient, ASCENDING
import time

class BDD:
    def __init__(self):
        # Connexion à MongoDB
        self.client = MongoClient('localhost', 27017)
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
            self.queue.insert_one({"url": url, "date": date})
        
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
            return [x["url"] for x in self.queue.find().limit(limit)]