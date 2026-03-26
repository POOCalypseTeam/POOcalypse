# ==== Tags ==== #
CANT_PASS = 1       # Impossible de passer a travers
TRIGGER   = 2       # Déclenche un événement au passage
    

class Collisions:
    """
    Cette classe permet de répertorier toutes les collisions du jeu, avec différentes couches et différentes actions lorsqu'il y a en effet collision
    """
    
    def __init__(self):
        pass
    
    def add_collider(self, collider, tag_code):
        pass
    
    def remove_collider(self, collider):
        pass
    
    def resolve_collision(self, position):
        pass