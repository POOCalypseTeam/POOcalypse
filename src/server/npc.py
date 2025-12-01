import sqlite3

from web.main_web import add_image, remove_html

def dialog_parse(dialog: str) -> list:
    """
    Lit la chaine de caracteres dialogues et la transcrit en une liste selon le format suivant:
    
    L'indice dans la liste correspond a l'etape dans le dialogue
    
    Chaque element de cette liste est un tuple au format (TEXTE_NPC, CHOIX_USER), avec:
    
    - TEXTE_NPC: Le texte dit par le NPC
    
    - CHOIX_USER: Le dictionnaire donnant la liste des choix comme cles et les indices dans la liste comme valeurs
    """
    dialogs = []
    
    link = sqlite3.connect("dialog")
    base = link.cursor()
    
    # On part de dialogs, avec l'id {dialog} pour prendre le exchange de start
    # On cherche donc dans choices les lignes avec exchange_id=start
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
