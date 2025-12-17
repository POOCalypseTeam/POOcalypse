import sqlite3

import wsinter
from web.main_web import add_image, change_text

DIALOGS_PATH = "content/data/lang/%LANG%/dialogs.db"

def explore_choices(cursor: sqlite3.Cursor, dialogs: list, exchange_id: int, parent: int = 0, ids_dict: dict = {}):
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
    if ids_dict == {}:
        ids_dict[exchange_id] = 0
    
    cursor.execute("SELECT sentence FROM exchanges WHERE id=? LIMIT 1;", (exchange_id,))
    sentence = cursor.fetchone()[0]
    
    dialogs.append((sentence, {}))
    
    cursor.execute("SELECT sentence, next_exchange FROM choices WHERE exchange_id=?;", (exchange_id,))
    data = cursor.fetchall()
    
    if len(data) == 0:
        return
        
    for choice in data:
        # On veut créer un dictionnaire qui associe l'id (choice[1]) dans la BD avec l'indice
        exploring = False
        if not choice[1] in ids_dict:
            exploring = True
            ids_dict[choice[1]] = len(dialogs)
        dialogs[parent][1][choice[0]] = ids_dict[choice[1]]
        if exploring:
            explore_choices(cursor, dialogs, choice[1], ids_dict[choice[1]], ids_dict)

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
    
    explore_choices(base, dialogs, data[0])
    
    return dialogs

class Interactable:
    def interact(self):
        pass
    
    def is_opened(self):
        return False
    
    def key(self, key: str):
        pass

class Npc(Interactable):
    def __init__(self, ws: wsinter.Inter, position: tuple, img_path: str, dialogs: str = "", distance: int = 30):
        self.ws = ws
        
        self.x = position[0]
        self.y = position[1]
        self.distance = distance
        
        if dialogs != "":
            """Liste de tuples de chaine et de dictionnaire"""
            self.dialogs: list[tuple[str, dict[str, int]]] = dialog_parse(dialogs)
            # Indice dans self.dialogs, il evolue au cours des echanges
            self.dialog_step: int = 0
            # Choix possibles pour l'utilisateur
            self.choices = self.get_dialog()[1].keys()
            # Indice das self.choices
            self.choice: int = 0
        
        self.opened = False
        
        self.id = add_image(img_path, (self.x, self.y))
        
    def interact(self):
        """
        Implementation de la methode interact() definie dans Interactable
        
        Cette methode est appelee lors de l'appui de la touuche d'interaction
        
        Ici, elle affiche le dialogue a l'ecran
        """
        self.opened = True
        self.ws.attributs("dialogs", style={"display":"grid"})
        
        # On remet le dialogue au debut
        self.dialog_step = 0
        self.choices = list(self.get_dialog()[1].keys())
        self.choice = 0
        
        dialog = self.get_dialog()
        change_text("dialog-content", dialog[0])
        
        self._display_dialog()
        
    def is_opened(self):
        return self.opened
    
    def key(self, key: str):
        if key == 'ArrowLeft':
            self.ws.attributs(self.choices[self.choice], style={"text-decoration":"none"})
            self.choice -= 1
            if self.choice < 0:
                self.choice = len(self.choices) - 1
            self.ws.attributs(self.choices[self.choice], style={"text-decoration":"underline"})
        elif key == 'ArrowRight':
            self.ws.attributs(self.choices[self.choice], style={"text-decoration":"none"})
            self.choice += 1
            if self.choice >= len(self.choices):
                self.choice = 0
            self.ws.attributs(self.choices[self.choice], style={"text-decoration":"underline"})
        elif key == 'Enter':
            if self.dialog_step >= len(self.dialogs) or len(self.choices) == 0:
                self.opened = False
                self.ws.attributs("dialogs", style={"display":"none"})
                return
            self.dialog_step = self.get_dialog()[1][self.choices[self.choice]]
            self.choices = list(self.get_dialog()[1].keys())
            self.choice = 0
            self._display_dialog()
            
    def _display_dialog(self):
        self.ws.inner_text("dialog-content", self.get_dialog()[0])
        
        self.ws.remove_children("choices")
        
        for choice in list(self.choices):
            style = {}
            if choice == self.choices[self.choice]:
                style["text-decoration"] = "underline"
            self.ws.insere(choice, "li", style=style, parent="choices")
            self.ws.inner_text(choice, choice)
        
    def get_dialog(self):
        return self.dialogs[self.dialog_step]
        
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
