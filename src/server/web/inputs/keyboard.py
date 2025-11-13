class KEvent:
    """
    Evenement clavier
    """
    
    def __init__(self, state: str, keys: list, handler: callable):
        self.state = state
        self.keys = keys
        self.handler = handler
        
    # Ne regarde pas les touches de modification (Alt, Ctrl, Shift, etc.)
    def match(self, state: str, key: list):
        """
        Verifie si l'entree donnee correspond a cet evenement et l'appelle si c'est le cas
        Renvoie True si l'evenement correspond, False sinon
        """
        if state == self.state and key[5] in self.keys:
            self.handler(key[5])
            return True
        return False

events = []

def add_event(handler: callable, state: str, keys: list):
    """
    Parametres :
        - handler: fonction appelee lorsque les conditions sont remplies
    
        - state: 
            - "D" si la touche est pressee
            - "U" si la touche est relachee
        
        - keys: liste de chaines de caractères représentant les touche declenchant l'evenement sur un clavier standard Qwerty
        
    Ajoute cet evenement a la liste des evenements
    """
    event = KEvent(state, keys, handler)
    events.append(event)    
    
def remove_event(handler: callable, state: str, keys: list):
    """
    Parametres :
        - handler: fonction appelee lorsque les conditions sont remplies
    
        - state: 
            - "D" si la touche est pressee
            - "U" si la touche est relachee
        
        - keys: liste de chaines de caractères représentant les touche declenchant l'evenement sur un clavier standard Qwerty
        
    Renvoie True s'il existait un tel evenement, False avec un message d'erreur sinon
    """
    event = KEvent(state, keys, handler)
    try:
        events.remove(event)    
    except ValueError:
        print("ValueError: Aucun evenement de la sorte existe!")
        return False
    return True

def handle_input(state: str, key: list):
    """
    Parametres :
        - state: 
            - "D" si la touche est pressee
            - "U" si la touche est relachee

        - key: La liste [altKey,ctrlKey,shiftKey,metaKey,key,code,repeat,timeStamp]
            - altKey,ctrlKey,shiftKey,metaKey : booléens indiquant si Alt, Control, Shift et Meta sont pressées
            - key : chaine de caractères représentant la saisie de caractère effectuée
            - code : chaine de caractères représentant la touche pressée sur un clavier standard Qwerty
            - repeat : booléen indiquant si la touche est en train d'être maintenue
            - timeStamp : entier donnant la chronologie des événements
        
    Redirige les evenements vers les bons gestionnaires
    """
    for event in events:
        event.match(state, key)
