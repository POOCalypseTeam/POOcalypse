# ==== Tags ==== #
CANT_PASS = 1       # Impossible de passer a travers
TRIGGER   = 2       # Déclenche un événement au passage
MOVABLE   = 4       # Possible de bouger le collider (ex: joueur, ennemis)

class Collisions:
    """
    Cette classe permet de répertorier toutes les collisions du jeu, avec différentes couches et différentes actions lorsqu'il y a en effet collision
    """
    
    def __init__(self):
        self.colliders = []
        self.to_check = []
    
    def add_collider(self, collider: tuple[int, int, int, int], tag_code: int, handler: callable = None) -> None:
        """
        Permet d'ajouter un rectangle qui fait office de collider

        Parametres:
            - collider: Position sur la carte, sous la forme de tuple (X1, Y1, X2, Y2)

            - tag_code: entier décrivant le comportement du collider

            - handler: fonction a appeler si le tag_code contient TRIGGER

        Leve une erreur lorsque le tag_code a TRIGGER mais qu'il n'y a pas de handler, ou l'inverse
        """
        if tag_code & TRIGGER and (handler == None or type(handler) != callable):
            raise ValueError("Le code est TRIGGER mais il n'y a pas de handler")
        if (handler != None and type(handler) == callable) and not tag_code & TRIGGER:
            raise ValueError("Il y a un handler mais le code n'est pas TRIGGER")
        pass
    
    def remove_collider(self, collider):
        """
        Enleve ce collider de la liste des collider
        """
        pass

    def attempt_movement(self, collider, movement):
        """
        Ajoute ce mouvement a la file de mouvement qu'il faut vérifier

        Lorsque self.resolve_collision est appelé, il essaie tous les mouvements de la file et les valide ou non
        """
    
    def resolve_collision(self):
        """
        Appelée par la boucle principale

        Vérifie pour chaque mouvement de la liste s'il est valide ou non et s'il faut déclencher des événements
        """
        pass