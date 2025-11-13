class MEvent:
    def __init__(self):
        pass
    
    def match(self):
        pass
    
events = []

def add_event(handler: callable, state: str, buttons: list):
    """
    Ajoute un evenement
    
    Parametres:
        - handler : Fonction a appeler en cas de declenchement
        
        - state :
            - "D" lorsque le bouton est presse
            - "U" lorsque le bouton est relache
            
        - buttons : Liste des boutons pour lesquels handler est appelé
    """
    pass

def remove_event():
    pass

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
