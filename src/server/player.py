from web.main_web import add_image, change_dimensions, get_window_size, change_image
from random import randint
from time import sleep

IMG_STOP1 = 'assets/spritesheets/blonde_man/blonde_man_001.png'
IMG_STOP2 = 'assets/spritesheets/blonde_man/blonde_man_002.png'
IMG_STOP3 = 'assets/spritesheets/blonde_man/blonde_man_003.png'
IMG_STOP4 = 'assets/spritesheets/blonde_man/blonde_man_004.png'
STOP = [IMG_STOP1, IMG_STOP2, IMG_STOP3, IMG_STOP4]

PNG_PATH = 'assets/spritesheets/blonde_man/blonde_man_000.png'

IMG_LEFT1 = 'assets/spritesheets/blonde_man/blonde_man_005.png'
IMG_LEFT2 = 'assets/spritesheets/blonde_man/blonde_man_006.png'
IMG_LEFT3 = 'assets/spritesheets/blonde_man/blonde_man_007.png'
IMG_LEFT4 = 'assets/spritesheets/blonde_man/blonde_man_008.png'
LEFT = [IMG_LEFT1, IMG_LEFT2, IMG_LEFT3, IMG_LEFT4]

IMG_RIGHT1 = 'assets/spritesheets/blonde_man/blonde_man_009.png'
IMG_RIGHT2 = 'assets/spritesheets/blonde_man/blonde_man_010.png'
IMG_RIGHT3 = 'assets/spritesheets/blonde_man/blonde_man_011.png'
IMG_RIGHT4 = 'assets/spritesheets/blonde_man/blonde_man_012.png'
RIGHT = [IMG_RIGHT1, IMG_RIGHT2, IMG_RIGHT3, IMG_RIGHT4]

IMG_TOP1 = 'assets/spritesheets/blonde_man/blonde_man_013.png'
IMG_TOP2 = 'assets/spritesheets/blonde_man/blonde_man_014.png'
IMG_TOP3 = 'assets/spritesheets/blonde_man/blonde_man_015.png'
IMG_TOP4 = 'assets/spritesheets/blonde_man/blonde_man_016.png'
TOP = [IMG_TOP1, IMG_TOP2, IMG_TOP3, IMG_TOP4]

IMG_BOTTOM1 = 'assets/spritesheets/blonde_man/blonde_man_017.png'
IMG_BOTTOM2 = 'assets/spritesheets/blonde_man/blonde_man_018.png'
IMG_BOTTOM3 = 'assets/spritesheets/blonde_man/blonde_man_019.png'
IMG_BOTTOM4 = 'assets/spritesheets/blonde_man/blonde_man_020.png'
BOTTOM = [IMG_BOTTOM1, IMG_BOTTOM2, IMG_BOTTOM3, IMG_BOTTOM4]

IMG = [LEFT, RIGHT, TOP, BOTTOM, STOP]
IMG_SIZE = 32
MOVE_AMOUNT = 10
MIN_X = 0
MIN_Y = 0
ANIMATION_UPDATE_FREQUENCY = 32

# Contient le joueur
class Player:
    def __init__(self, position: tuple):
        self.x = position[0]
        self.y = position[1]
        # TODO: Resize hitbox to fit character best
        self.width = IMG_SIZE
        self.height = IMG_SIZE
        self.id = add_image(IMG_STOP1, (self.x, self.y))
        self.id2 = add_image(PNG_PATH, (0,0))
        self.r = 0
        self.l = 0
        self.b = 0
        self.t = 0
        self.s = 0
        for i in range(5):
            for j in range(4):
                change_image(self.id2, IMG[i][j])
                sleep(0.1)
        change_image(self.id2, PNG_PATH)
        
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
                self.r += 1
                self.r %= ANIMATION_UPDATE_FREQUENCY
                IMG_RIGHT = RIGHT[self.r // 8]
                change_image(self.id, IMG_RIGHT)
            elif movement[0] < 0:
                self.l += 1
                self.l %= ANIMATION_UPDATE_FREQUENCY
                IMG_LEFT = LEFT[self.l // 8]
                change_image(self.id, IMG_LEFT)
            elif movement[1] > 0 :
                self.b += 1
                self.b %= ANIMATION_UPDATE_FREQUENCY
                IMG_BOTTOM = BOTTOM[self.b // 8]
                change_image(self.id, IMG_BOTTOM)
            elif movement[1] < 0:
                self.t += 1
                self.t %= ANIMATION_UPDATE_FREQUENCY
                IMG_TOP = TOP[self.t // 8]
                change_image(self.id, IMG_TOP)
        else:
            self.s += 1
            self.s %= ANIMATION_UPDATE_FREQUENCY
            IMG_STOP = STOP[self.s // 8]
            change_image(self.id, IMG_STOP)
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