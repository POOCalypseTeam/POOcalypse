from web.main_web import add_image, change_dimensions, get_window_size
from random import randint

IMG_PATH = "assets/spritesheets/blonde_man/blonde_man_001.png"
IMG_SIZE = 32
MOVE_AMOUNT = 2
MIN_X = 0
MIN_Y = 0

# Contient le joueur
class Player:
    def __init__(self, position: tuple):
        self.x = position[0]
        self.y = position[1]
        # TODO: Resize hitbox to fit character best
        self.width = IMG_SIZE
        self.height = IMG_SIZE
        self.id = add_image(IMG_PATH, (self.x, self.y))
        
    def move(self, movement: tuple):
        """
        Mouvement sur la position du joueur
        
        Parametres:
        
            - movement : tuple de la forme (x, y) indiquant la quantite de mouvement dans chacune des directions
        """
        window_size = get_window_size()
        
        self.x += movement[0]
        self.x = min(self.x, window_size[0] - self.width)
        self.x = max(MIN_X, self.x)
        
        self.y += movement[1]
        self.y = min(self.y, window_size[1] - self.height)
        self.y = max(MIN_Y, self.y)
        
        self.render()
        
    def move_input(self, key):
        """
        Recupere l'evenement d'appui de touche pour bouger le joueur
        """
        match key:
            case "KeyW":
                self.move((0, -MOVE_AMOUNT))
            case "KeyA":
                self.move((-MOVE_AMOUNT, 0))
            case "KeyS":
                self.move((0, MOVE_AMOUNT))
            case "KeyD":
                self.move((MOVE_AMOUNT, 0))
                
    def move_random(self, button):
        if button[1] == 0:
            self.move((randint(-100, 100), randint(-100, 100)))
        
    def render(self):
        change_dimensions(self.id, (self.x, self.y))