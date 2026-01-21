class MEvent:
    """
    Evenement souris
    """
    def __init__(self, state: str, ids: list, handler: callable):
        self.state = state
        self.ids = ids
        self.handler = handler
    
    def match(self, state: str, button: list):
        if state == self.state and button[0] in self.ids:
            self.handler(button)
            return True
        return False

# TODO: Utiliser le meme principe que inputs.Keyboard, mais pour la souris
events = []

def add_event(handler: callable, state: str, ids: list):
    """
    Parametres:
        - handler: Fonction a appeler en cas de declenchement
        
        - state: Une chaine de caractere donnant l'etat du bouton:
            - "D": Bouton appuye
            - "U": Bouton relache
            
        - ids: Liste des IDs des objets lancant un appel     
           
    Ajoute un evenement
    """
    event = MEvent(state, ids, handler)
    events.append(event)

def remove_event(handler: callable, state: str, ids: list):
    event = MEvent(state, ids, handler)
    try:
        events.remove(event)
    except ValueError:
        print("ValueError: Aucun evenement de la sorte n'existe!")
        return False
    return True

def handle_input(state: str, button: list):
    """
    Définit le gestionnaire de la souris
    Paramètres :
        - handler : fonction à deux paramètres appelée lors d'un événement de la souris

    Valeur renvoyée : None

    Pour chaque clic, deux événements ont lieu :
        - un appel handler("D",p) lorsqu'un bouton est pressé
        - un appel handler("U",p) lorsqu'un bouton est relâché.
        
    Le paramètre p passé à handler est la liste [target.id,buttons,layerX,layerY]
        - target.id : attribut id de l'objet qui a reçu le clic
        - buttons   : entier qui indique quels boutons sont pressés
        - layerX,layerY : coordonnées, en pixels, relativement au coin supérieur gauche de la page
    """
    for event in events:
        event.match(state, button)
