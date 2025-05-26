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
        # Création de queue
        self.queue = self.db['queue']
        self.queue.create_index([("url", ASCENDING)], unique=True)
        # Création de last_visited
        self.last_visited = self.db['last_visited']
        self.last_visited.create_index([("url", ASCENDING)], unique=True)
        # Création de mots_texte
        self.mots_texte = self.db['mots_texte']
        self.mots_titles = self.db['mots_titles']

    def add_to_queue(self, url, date):
        try:
            if not self.queue.find_one({"url": url})
                self.queue.insert_one({"url": url, "date": date})
        except errors.DuplicateKeyError:
            # Gérer le cas où l'URL existe déjà
            pass
        
    def add_to_last_visited(self, url, date):
        try:
            self.last_visited.insert_one({"url": url, "date": date})
        except errors.DuplicateKeyError:
            # Gérer le cas où l'URL existe déjà
            pass
    
    def add_to_crawled(self, url, date):
        self.crawled.insert_one({"url": url, "date": date})
        
    def check_if_crawled(self, url):
        return self.webpages.find_one({"url": url})
        
    def get_queue(self, limit):
        urls = [x["url"] for x in self.queue.find().limit(limit)]
        for url in urls:
            self.queue.delete_one({"url": url})
        return urls
    
    def get_last_visited(self, url, limit):
        return self.last_visited.find_one({"url": url})
    
    def save_page(self, page_data):
        self.webpages.insert_one(page_data)
    
    def add_nb_mots(self, page, nb_mots):
        self.webpages.update_one({"_id": page['_id']}, {"$set": {"nb_mots": nb_mots}})
    # Récupère un site
    def get_webpage(self, url):
        return self.webpages.find_one({"url": url})
    # Récupère toutes les sites
    def get_webpages(self):
        return self.webpages.find()
    
    def add_mots_texte(self, data):
        self.mots_texte.insert_many(data)

    def add_mots_titles(self, data):
        self.mots_titles.insert_many(data)

    def get_content(self, url):
        return self.get_webpage(url)['content']

    def update_webpage(self, page):
        self.webpages.replace_one({'_id': page['_id']}, page)