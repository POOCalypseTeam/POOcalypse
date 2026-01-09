from web.main_web import add_image, change_dimensions, get_window_size, change_image
from random import randint
from time import sleep

IMG_PATH = 'assets/spritesheets/blonde_man/blonde_man_001.png'
IMG_LEFT = 'assets/spritesheets/blonde_man/blonde_man_005.png'
IMG_RIGHT = 'assets/spritesheets/blonde_man/blonde_man_009.png'
IMG_TOP = 'assets/spritesheets/blonde_man/blonde_man_013.png'
IMG_BOTTOM = 'assets/spritesheets/blonde_man/blonde_man_017.png'
IMG_SIZE = 32
MOVE_AMOUNT = 10
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
        self.id2 = add_image(IMG_PATH, (0,0))
        change_image(self.id2, IMG_TOP)
        sleep(0.1)
        change_image(self.id2, IMG_LEFT)
        sleep(0.1)
        change_image(self.id2, IMG_RIGHT)
        sleep(0.1)
        change_image(self.id2, IMG_BOTTOM)
        
        
        self.movement_vector = [0, 0]
        # Changés par le sol / environnement
        self.max_movement = (1, 1)
        self.friction_coef = 0.8
        
    def move_range(self, movement: tuple):
        self.movement_vector[0] += movement[0]
        if self.movement_vector[0] < 0 and self.movement_vector[0] < -1 * self.max_movement[0]:
            self.movement_vector[0] = -1 * self.max_movement[0]
        if self.movement_vector[0] > 0 and self.movement_vector[0] > self.max_movement[0]:
            self.movement_vector[0] = self.max_movement[0]

        self.movement_vector[1] += movement[1]
        if self.movement_vector[1] < 0 and self.movement_vector[1] < -1 * self.max_movement[1]:
            self.movement_vector[1] = -1 * self.max_movement[1]
        if self.movement_vector[1] > 0 and self.movement_vector[1] > self.max_movement[1]:
            self.movement_vector[1] = self.max_movement[1]
            
    def update(self, delta_time: float, keys: list):
        """
        delta_time est le temps en secondes depuis la derniere update, il sert de coefficient sur la vitesse de deplacement notamment
        """
        # On applique le vecteur mouvement sur la position, en tenant compte des inputs et de la friction s'il n'y a pas d'inputs
        # Tant que la friction n'est pas supérieure à 1, on a pas besoin de vérifier avec le vecteur max_movement, car le mouvement diminue,
        # Mais si dans le futur il y a changement sur ca il faudra check tout le temps
        movement = self._process_keys(keys)
        self.movement_vector[0] *= self.friction_coef
        self.movement_vector[1] *= self.friction_coef
        if movement != [0, 0]:
            movement[0] *= delta_time
            movement[1] *= delta_time
            self.move_range(movement)        
            if movement[0] > 0:
                change_image(self.id, IMG_RIGHT)
            elif movement[0] < 0:
                change_image(self.id, IMG_LEFT)
            elif movement[1] > 0 :
                change_image(self.id, IMG_BOTTOM)
            elif movement[1] < 0:
                change_image(self.id, IMG_TOP)
        
        self.move(self.movement_vector)
        self.render()
        
    def _process_keys(self, keys: dict) -> list:
        """
        keys -- liste de touches appuyees, identifiees par leur code
        
        Renvoie un tuple definissant le mouvement selon le mouvement
        """
        move = [0, 0]
        if "KeyW" in keys:
            move[1] -= MOVE_AMOUNT
        if "KeyA" in keys:
            move[0] -= MOVE_AMOUNT
        if "KeyS" in keys:
            move[1] += MOVE_AMOUNT
        if "KeyD" in keys:
            move[0] += MOVE_AMOUNT
        return move

        
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
        self.render()
        
    def render(self):
        change_dimensions(self.id, (self.x, self.y))