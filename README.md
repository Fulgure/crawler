# API Fulgure

Ce répertoire appartiens au projet Fulgure un moteur de recherche respectant les donnée de l'utilisateur.

## Fonctionnalité

 - Système de récupération d'url
 - Collecte d'information sur les pages
 - Indexation (Collecte du titre, Mot clé, Description, PageRank)

---

## 🚀 Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/Fulgure/crawler.git
cd crawler
```
### 2. Crée le .env a partir du .env.example
Commande Unix
```bash
cp .env.example .env
```

Commande PowerShell
```bash
Copy-Item .env.example .env
```

Commande CMD
```bash
copy .env.example .env
```

### 3. Modifier le .env (optionnel)
Actuellement la crawler pointe sur le serveur mongoDB a distance mais vous pouvez le pointer sur un serveur mongoDB local

```bash
DATABASE_URL={URL_DU_SERVEUR_LOCAL}
```

### 4. Installer les dépendence python

```bash
pip install -r requirements.txt
```

### 5. Lancement de l'API
```bash
python3 crawler.py
```