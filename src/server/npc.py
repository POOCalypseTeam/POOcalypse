import sqlite3

#from web.main_web import add_image, remove_html

DIALOGS_PATH = "content/data/lang/%LANG%/dialogs.db"

def explore_choices(cursor: sqlite3.Cursor, dialogs: list, exchange_id: int, parent: int):
    """
    Fonction recursive qui lit la base de donnees pour trouver tous les choix descendants de `exchange_id`
    
    Cette fonction est appelee a l'origine avec l'id `start` issu de la table dialogs
    
    Les appels recursifs s'arretent lorqu'aucun choix ne decoule de `exchange_id`
    
    Parametres:
    
    - `cursor`: curseur sqlite3 qui permet de naviguer dans le SGBD
    
    - `dialogs`: liste de tuples de dictionnaires, modifie en place
    
    - `exchange_id`: l'id de l'echange a chercher dans la base de donnees
    
    - `parent`: l'indice du parent, echange qui a donne lieu au choix actuel, dans `dialogs`
    """
    # On cherche tous les choix dans le SGBD avec l'id
    
    cursor.execute("SELECT sentence FROM exchanges WHERE id=? LIMIT 1;", (exchange_id,))
    sentence = cursor.fetchone()[0]
    
    dialogs.append((sentence, {}))
    
    cursor.execute("SELECT sentence, next_exchange FROM choices WHERE exchange_id=?;", (exchange_id,))
    data = cursor.fetchall()
    
    if len(data) == 0:
        return
        
    for choice in data:
        # Attention, si les echanges dans choices forment une boucle, il y a une boucle infinie ici
        # Il faudrait regarder quels ids sont passes pour ne pas les repasser une deuxieme fois

        dialogs[parent][1][choice[0]] = choice[1]
        explore_choices(cursor, dialogs, choice[1], len(dialogs))  

def dialog_parse(dialog: str) -> list[tuple[str, dict[str, int]]]:
    """
    Recupere dans la base de donnees tous les echanges (textes et choix) portant sur le dialogue `dialog`

    Parametres:
    
    - `dialog`: chaine de caracteres donnant l'id du dialogue dans le base de donnee
    
    Renvoie la liste de tuples de la forme (TEXTE, CHOIX):
    
    - TEXTE etant une chaine de caracteres representant ce que peut dire le NPC
    
    - CHOIX etant un dictionnaire avec en cles les choix possibles et en valeurs l'indice dans la liste vers le prochain texte
    """
    dialogs = []

    link = sqlite3.connect(DIALOGS_PATH.replace("%LANG%", "fr"))
    base = link.cursor()
    
    # On part de dialogs, avec l'id {dialog} pour prendre le exchange de start
    # On limite a 1 pour etre sur, meme si dans tous les cas on en prend qu'un
    base.execute("SELECT start FROM dialogs WHERE id=? LIMIT 1;", (dialog,))
    data = base.fetchone()
    
    # Pile de tous les dialogues pour lesquels il faut encore aller chercher les prochains echanges
    exchanges_stack: list[int] = []
    exchanges_stack.append(data[0])
    
    # On cherche donc dans choices les lignes avec exchange_id=start
    # TODO: Fix, ne marche pas car IDs dans SGBD pas pareil que l'indice dans dialogs
    # Il faut faire une fonction recursive qui parcourt chaque choix jusqu'a ce qu'il n'y ait plus de choix
    # Ainsi les indices dans dialogs match et ceux dans le SGBD servet juste pour naviguer le SGBD
    while len(exchanges_stack) > 0:
        # TODO: Optimiser pour eviter de deplacer la liste a chaque fois, avec retrait puis ajout a chaque iteration
        exchange = exchanges_stack.pop()
        
        # On recupere la phrase du NPC
        base.execute("SELECT sentence FROM exchanges WHERE id=? LIMIT 1;", (exchange,))
        data = base.fetchall()
        
        element = (data[0][0], {})
        
        # On recupere tous les choix possibles pour cette phrase
        base.execute("SELECT sentence, next_exchange FROM choices WHERE exchange_id=?;", (exchange,))
        data = base.fetchall()
        
        # Pour chaque choix on ajoute au dictionnaire la paire texte_choix:prochain_echange
        for choice in data:
            element[1][choice[0]] = choice[1]
            exchanges_stack.append(choice[1])
            
        dialogs.append(element)
            
        
    # Puis on ajoute a dialogs au premier indice (exchanges[start], {choices[0].sentence: choices[0].next_exchange, choices[1].sentence: choices[1].next_exchange})
    # Tout en ajoutant a une pile les prochains "start" a traiter, qui sont choices[i].next_exchange
    
    return dialogs

class Npc:
    def __init__(self, position: tuple, img_path: str, dialogs: str = "", distance: int = 50):
        self.x = position[0]
        self.y = position[1]
        
        if dialogs != "":
            try:
                # TODO: Remplacer fr par la langue
                file_path = "content/data/lang/fr/dialogs/" + dialogs
                file = open(file_path, "r")
            except FileNotFoundError:
                print(f"Impossible d'ouvrir le fichier dialogues: {file_path}")
                
            self.dialogs = dialog_parse(file.read())
            self.dialog_step = 0
        
        self.distance = distance
        
        self.id = add_image(img_path, (self.x, self.y))
        
    def get_dialog(self):
        return self.dialogs[self.dialog_step]
        
    def hide(self):
        remove_html(self.id)
        
    def within_distance(self, position: tuple) -> bool:
        """
        Regarde si la position donnée est à portée du NPC
        
        On ne regarde pas la distance euclidienne mais la distance coordonnée par coordonnée
        
        Donc en réalité la distance maximale possible est plus grande que celle attendue de base
        
        Renvoie True si dans la distance, False sinon
        """
        if self.x - self.distance > position[0] or self.x + self.distance < position[0]:
            return False
        if self.y - self.distance > position[1] or self.y + self.distance < position[1]:
            return False
        return True
