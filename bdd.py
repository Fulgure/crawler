from pymongo import MongoClient, ASCENDING
import time

class BDD:
    def __init__(self):
        # Connexion à MongoDB
        self.client = MongoClient('localhost', 27017)
        # Création d'une nouvelle base de données
        self.db = self.client['fulgure']
        