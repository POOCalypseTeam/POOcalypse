from web.main_web import add_image, remove_html

class NPC:
    def __init__(self, position: tuple, img_path: str, distance: int = 50):
        self.x = position[0]
        self.y = position[1]
        self.distance = 10
        self.id = add_image(img_path, (self.x, self.y))
        
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
