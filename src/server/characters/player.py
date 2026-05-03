from time import sleep
from math import pi, atan2, sin, cos
import web_helper

from .weapon import Weapon
from .enemy import Enemy

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
IMG_SIZE = 64
MOVE_AMOUNT = 32
MIN_X = 0
MIN_Y = 0
ANIMATION_UPDATE_FREQUENCY = 32

# Contient le joueur
class Player:
    def __init__(self, helper: web_helper.Helper, map_center: tuple):
        self.helper = helper
        # X1, Y1, X2, Y2 pour l'image dans sa taille originale, il faut appliquer le zoom
        self.hitbox = (9, 26, 22, 32)
        self.width = IMG_SIZE
        self.height = IMG_SIZE
        self.x = map_center[0]
        self.y = map_center[1]
        self.id2 = self.helper.add_image(PNG_PATH, (0,0), size=(64, 64), parent="player")
        self.r = 0
        self.l = 0
        self.b = 0
        self.t = 0
        self.s = 0
        for i in range(5):
            for j in range(4):
                self.helper.change_image(self.id2, IMG[i][j])
                sleep(0.1)
        self.helper.change_image(self.id2, PNG_PATH)
        w,h = self.helper.ws.get_window_size()
        self.id = self.helper.add_image(IMG_STOP1, ((w - self.width) / 2, (h - self.height) / 2), size=(64, 64), parent="player")
        
        self.health = 5
        self.max_health = 5
        self.dead = False

        self.weapon = Weapon(10, 40, 0.3)
        
        self.movement_vector = [0, 0]
        self.friction_coef = 0.8
    
    def update(self, delta_time: float, keys: list, enemies: list[Enemy]) -> tuple[float, float]:
        if 'KeyR' in keys:
            self.attack(enemies)
        return self.update_movement(delta_time, keys)
    
    def update_movement(self, delta_time: float, keys: list) -> tuple[float, float]:
        """
        delta_time est le temps en secondes depuis la derniere update, il sert de coefficient sur la vitesse de deplacement notamment
        """
        # On applique le vecteur mouvement sur la position, en tenant compte des inputs et de la friction s'il n'y a pas d'inputs
        # Tant que la friction n'est pas supérieure à 1, on a pas besoin de vérifier avec le vecteur max_movement, car le mouvement diminue,
        # Mais si dans le futur il y a changement sur ca il faudra check tout le temps
        coef = delta_time * self.friction_coef
        self.movement_vector[0] *= coef
        self.movement_vector[1] *= coef
        self.movement_vector = [round(self.movement_vector[0], 3), round(self.movement_vector[1], 3)]
        movement_direction = self._process_move_keys(keys)
        if movement_direction != [0, 0]:
            angle = atan2(movement_direction[1], movement_direction[0])
            movement = (cos(angle) * MOVE_AMOUNT * delta_time * 2, sin(angle) * MOVE_AMOUNT * delta_time * 2)
            self.movement_vector[0] += movement[0]
            self.movement_vector[1] += movement[1] 
            if abs(movement[0]) > abs(movement[1]):
                if movement[0] > 0:
                    self.r += 1
                    self.r %= ANIMATION_UPDATE_FREQUENCY
                    IMG_RIGHT = RIGHT[self.r // 8]
                    self.helper.change_image(self.id, IMG_RIGHT)
                elif movement[0] < 0:
                    self.l += 1
                    self.l %= ANIMATION_UPDATE_FREQUENCY
                    IMG_LEFT = LEFT[self.l // 8]
                    self.helper.change_image(self.id, IMG_LEFT)
            elif movement[1] > 0 :
                self.b += 1
                self.b %= ANIMATION_UPDATE_FREQUENCY
                IMG_BOTTOM = BOTTOM[self.b // 8]
                self.helper.change_image(self.id, IMG_BOTTOM)
            else:
                self.t += 1
                self.t %= ANIMATION_UPDATE_FREQUENCY
                IMG_TOP = TOP[self.t // 8]
                self.helper.change_image(self.id, IMG_TOP)
        else:
            self.s += 1
            self.s %= ANIMATION_UPDATE_FREQUENCY
            IMG_STOP = STOP[self.s // 8]
            self.helper.change_image(self.id, IMG_STOP)

        return self.movement_vector
        
    def _process_move_keys(self, keys: dict) -> list:
        """
        keys -- liste de touches appuyees, identifiees par leur code
        
        Renvoie un tuple definissant le mouvement selon le mouvement
        """
        move = [0, 0]
        if "KeyW" in keys:
            move[1] -= 1
        if "KeyA" in keys:
            move[0] -= 1
        if "KeyS" in keys:
            move[1] += 1
        if "KeyD" in keys:
            move[0] += 1
        return move
    
    def get_position(self):
        """
        Renvoie la position du joueur (x,y) sur la page par rapport a son coin superieur gauche
        """
        return (self.x, self.y)
    
    def get_boundaries(self, mov):
        """
        Renvoie le tuple (X1, Y1, X2, Y2) qui definit la boite de collisions du joueur, attention elle ne correspond pas exactement au visuel du joueur, elle est plus petite
        """
        return [self.get_position()[i%2] + mov[i%2] + self.hitbox[i] * 2 for i in range(4)]
    
    def get_center_pos(self):
        """
        Renvoie la position du joueur (x,y) sur la page centree sur le joueur
        """
        x = int(self.x + self.width / 2)
        y = int(self.y + self.height / 2)
        return (x,y)
        
    def render(self, movement_vector):
        """
        Actualise la position du joueur sur la page avec le mouvement stocké dans self.movement_vector
        """
        self.y += movement_vector[1]
        self.x += movement_vector[0]
        # Pas besoin, c'est la map qui le fait, on a cependant toujours besoin de savoir ou est le joueur
        #self.helper.change_dimensions(self.id, (self.x, self.y))
        
    def hit(self, damage: float):
        """
        Fait des degats au joueur
        
        Parametres:
            - damage: un flottant donnant le nombre de PV que l'attaque doit infliger
        
        Renvoie True si le joueur est mort, False sinon
        """
        self.health = max(0, self.health - damage)
        if self.health == 0:
            self.dead = True
            # TODO: Faire quelque chose quand le joueur meurt, afficher un menu par exemple, pour l'instant il y a plus de mouvement
        return self.dead
    
    def attack(self, enemies: list[Enemy]):
        self.weapon.attack(enemies)
        
    def is_dead(self):
        """
        Renvoie True si le joueur est mort, False sinon
        """
        return self.dead
    
