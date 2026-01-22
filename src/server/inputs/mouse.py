class _MEvent:
    """
    Evenement souris
    """
    def __init__(self, state: str, ids: list, handler: callable):
        self.state = state
        self.ids = ids
        self.handler = handler
    
    def match(self, state: str, id:str, buttons: dict):
        if state == self.state and id in self.ids:
            self.handler(buttons)
            return True
        return False

from wsinter import Inter
class Mouse:
    def __init__(self, web_manager: Inter):
        web_manager.gestionnaire_souris(self.handle_input)
        
        self.pressed_buttons = {"L": False, "R": False, "M": False}
        self.events = []
        self.position = (0,0)

    def subscribe_event(self, handler: callable, state: str, ids: list):
        """
        Parametres:
            - handler: Fonction a appeler en cas de declenchement
            
            - state: Une chaine de caractere donnant l'etat du bouton:
                - "D": Bouton appuye
                - "U": Bouton relache
                Attention, le dictionnaire de boutons renvoye contient les touches appuyees
                
            - ids: Liste des IDs des objets lancant un appel     
            
        Ajoute cete evenement a la liste des evenements
        """
        event = _MEvent(state, ids, handler)
        self.events.append(event)

    def unsubscribe_event(self, handler: callable, state: str, ids: list):
        event = _MEvent(state, ids, handler)
        try:
            self.events.remove(event)
        except ValueError:
            print("ValueError: Aucun evenement de la sorte n'existe!")
            return False
        return True

    def handle_input(self, state: str, button: list):
        """
        Définit le gestionnaire de la souris
        Paramètres :
            - handler : fonction à deux paramètres appelée lors d'un événement de la souris

        Valeur renvoyée : None

        Pour chaque clic, deux événements ont lieu :
            - un appel handler("D",p) lorsqu'un bouton est pressé
            
            - un appel handler("U",p) lorsqu'un bouton est relâché.
            
        Le paramètre p passé à handler est la liste:
            - target.id: attribut id de l'objet qui a reçu le clic
            
            - buttons: entier qui indique quels boutons sont pressés
            1 pour gauche, 2 pour droite, 4 pour milieu, on en fait la somme
            
            - layerX,layerY: coordonnées, en pixels, relativement au coin supérieur gauche de la page
        """
        buttons = button[1]
        for i, b in enumerate(["M", "R", "L"]):
            if buttons >= 2 ** (2 - i):
                buttons -= 2 ** (2 - i)
                self.pressed_buttons[b] = True
            else:
                self.pressed_buttons[b] = False
                
        self.position = (button[2], button[3])
        
        for event in self.events:
            event.match(state, self.pressed_buttons)
            
    def get_buttons(self) -> tuple[dict[str, bool], tuple[int, int]]:
        """
        Renvoie le tuple tel que:
            - premier element: un dictionnaire representant pour chaque bouton de la souris, son etat
            
            - deuxieme element: un tuple indiquant la position (x,y) du dernier clic de la souris
        """
        return (self.pressed_buttons, self.position)
