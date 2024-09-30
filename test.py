from pymongo import MongoClient

try:
    # Remplacez par l'adresse IP publique de votre serveur MongoDB
    client = MongoClient('mongodb://85.215.128.3:27017/')
    client.admin.command('ping')
    print("Connexion réussie")
except Exception as e:
    print("Erreur de connexion :", e)
