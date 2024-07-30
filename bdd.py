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
        
