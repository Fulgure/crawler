from bdd import BDD
import re
from collections import defaultdict

class Indexation:
    def __init__(self):
        self.bdd = BDD()

    def add_number_of_words(self, url):
        page = self.bdd.get_webpage(url)
        texte = page.get('text')
        texte = texte.replace("œ", "oe")
        texte = texte.replace("æ", "ae")
        texte = re.sub(r"[^a-zA-ZÀ-ÿ ']", " ", texte)
        nb_mots = len(texte)
        self.bdd.add_nb_mots(page, nb_mots)
    
    def inverted_index_in_text(self, url):

        # Utiliser un dictionnaire pour un accès rapide aux mots
        inverted_index = defaultdict(lambda: defaultdict(int))

        page =self.bdd.get_webpage(url)
        texte = page.get('text')
        url = page.get('url')
        texte = texte.replace("œ", "oe")
        texte = texte.replace("æ", "ae")

        for mot in texte.split():
            mot = mot.lower()

            if "'" in mot:
                mot = mot.split("'")[-1]
            # Compter les occurrences directement dans le dictionnaire
            inverted_index[mot][url] += 1
        
        inverted_index_list = [{"mot": mot, "appear_in": [{"url": url, "occurrences": count} for url, count in urls.items()]} for mot, urls in inverted_index.items()]
        
        self.bdd.add_mots_texte(inverted_index_list)

    def inverted_index_in_titles(self, url):

        # Utiliser un dictionnaire pour un accès rapide aux mots
        inverted_index = defaultdict(lambda: defaultdict(int))

        page = self.bdd.get_webpage(url)
        title = page.get('title')
        url = page.get('url')
        title = title.replace("œ", "oe")
        title = title.replace("æ", "ae")

        for mot in title.split():
            mot = mot.lower()

            if "'" in mot:
                mot = mot.split("'")[-1]
            # Compter les occurrences directement dans le dictionnaire
            inverted_index[mot][url] += 1
        
        inverted_index_list = [{"mot": mot, "appear_in": [{"url": url, "occurrences": count} for url, count in urls.items()]} for mot, urls in inverted_index.items()]

        self.bdd.add_mots_titles(inverted_index_list)
    
    def page_rank(self, url, d = 0.85, iteration = 10):
        page_send = self.bdd.get_webpage(url)
        all_pages = list(self.bdd.get_webpages())

        for i in range(iteration):
            pr_updates = defaultdict(float)

            for page in all_pages:
                links_count = len(page['link_to'])

                if links_count == 0:
                    links_count = len(all_pages)

                for linked_page in page['link_to']:
                    pr_updates[linked_page] += page['PageRank'] / links_count

            sum = 0

            new_pr = (1 - d) + d * pr_updates[page_send['url']]
            sum += new_pr
            self.bdd.update_webpage(page_send, new_pr)

            

def calcul_pagerank(d = 0.85, iteration = 10):
    bdd = BDD()
    initial_pr = 1
    for page in bdd.get_webpages():
        bdd.update_webpage(page, initial_pr)
    
    for i in range(iteration):
        all_pages = list(bdd.get_webpages())

        pr_updates = defaultdict(float)


        for page in all_pages:
            links_count = len(page['link_to'])

            if links_count == 0:
                links_count = len(all_pages)

            for linked_page in page['link_to']:
                pr_updates[linked_page] += page['PageRank'] / links_count

        sum = 0

        for page in all_pages:
            new_pr = (1 - d) + d * pr_updates[page['url']]
            sum += new_pr
            bdd.update_webpage(page, new_pr)

#calcul_pagerank()
#inverted_index_in_text()
#inverted_index_in_titles()
#add_number_of_words()