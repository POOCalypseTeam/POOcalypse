from random import randint
from time import sleep
from math import sqrt, atan2, sin, cos
import web_helper

from .weapon import Weapon
from .enemy import Enemy


ANIM_STOP = 'assets/spritesheets/player/player_stop.gif'
ANIM_LEFT = 'assets/spritesheets/player/player_left.gif'
ANIM_BOTTOM = 'assets/spritesheets/player/player_bottom.gif'
ANIM_RIGHT = 'assets/spritesheets/player/player_right.gif'
ANIM_TOP = 'assets/spritesheets/player/player_top.gif'
ANIM_DEATH = 'assets/spritesheets/player/player_death.gif'
ANIM_ATTACK_TOP = 'assets/spritesheets/player/player_attack_top.gif'
ANIM_ATTACK_BOTTOM = 'assets/spritesheets/player/player_attack_bottom.gif'
ANIM_ATTACK_RIGHT = 'assets/spritesheets/player/player_attack_right.gif'
ANIM_ATTACK_LEFT = 'assets/spritesheets/player/player_attack_left.gif'

IMG_SIZE = 64
MOVE_AMOUNT = 50
MIN_X = 0
MIN_Y = 0
ANIM_ATTACK_DURATION = 0.550


# Contient le joueur
class Player:
    def __init__(self, helper: web_helper.Helper, position: tuple):
        self.helper = helper
        self.x = position[0]
        self.y = position[1]
        # TODO: Resize hitbox to fit character best
        self.width = IMG_SIZE
        self.height = IMG_SIZE
        self.id = self.helper.add_image(ANIM_STOP, (self.x, self.y), size=(64, 64), parent="player")
        self.r = 0
        self.l = 0
        self.b = 0
        self.t = 0
        self.s = 0
        self.att = False
        
        self.health = 5
        self.max_health = 5
        self.dead = False

        self.weapon = Weapon(10, 40, 0.3)
        
        self.movement_vector = [0, 0]
        # Changés par le sol / environnement
        self.max_movement = 2
        self.friction_coef = 0.8

    def move_range(self, movement: tuple):
        """
        Cette fonction ajoute a self.movement_vector le vecteur movement, passe en parametre
        
        Elle ajuste cette somme pour ne pas exceder le mouvement maximum
        """
        # On calcule la distance qui serait parcourue
        self.movement_vector[0] += movement[0]
        self.movement_vector[1] += movement[1]
        distance = sqrt(self.movement_vector[0] ** 2 + self.movement_vector[1] ** 2)
        if distance <= self.max_movement:
            return
        # On calcule l'angle de deplacement
        a = atan2(self.movement_vector[1], self.movement_vector[0])
        # On calcule les nouveaux x et y
        self.movement_vector[0] = cos(a)
        self.movement_vector[1] = sin(a)
    
    def update(self, delta_time: float, keys: list, enemies: list[Enemy]) -> tuple[float, float]:
        if 'KeyR' in keys:
            self.attack(enemies)
            self.att = True
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
        movement = self._process_move_keys(keys)
        delta_sum = 0
        if movement != [0, 0]:
            self.move_range(movement)        
            if movement[0] > 0:
                self.helper.change_image(self.id, ANIM_ATTACK_RIGHT if self.att else ANIM_RIGHT)
                delta_sum = delta_time
                while delta_sum < ANIM_ATTACK_DURATION:
                    delta_sum += delta_time
                self.att = False
                delta_sum = 0
            elif movement[0] < 0:
                self.helper.change_image(self.id, ANIM_ATTACK_LEFT if self.att else ANIM_LEFT)
                delta_sum = delta_time
                while delta_sum < ANIM_ATTACK_DURATION:
                    delta_sum += delta_time
                self.att = False
                delta_sum = 0
            elif movement[1] > 0 :
                self.helper.change_image(self.id, ANIM_ATTACK_BOTTOM if self.att else ANIM_BOTTOM)
                delta_sum = delta_time
                while delta_sum < ANIM_ATTACK_DURATION:
                    delta_sum += delta_time
                self.att = False
                delta_sum = 0
            elif movement[1] < 0:
                self.helper.change_image(self.id, ANIM_ATTACK_TOP if self.att else ANIM_TOP)
                delta_sum = delta_time
                while delta_sum < ANIM_ATTACK_DURATION:
                    delta_sum += delta_time
                self.att = False
                delta_sum = 0
        else:
            self.helper.change_image(self.id, ANIM_ATTACK_BOTTOM if self.att else ANIM_STOP)
            delta_sum = delta_time
            while delta_sum < ANIM_ATTACK_DURATION:
                delta_sum += delta_time
            self.att = False
            delta_sum = 0
            
        self.x += self.movement_vector[0]
        self.y += self.movement_vector[1]   

        self.render()
        return self.movement_vector
        
    def _process_move_keys(self, keys: dict) -> list:
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
        
    def get_position(self):
        """
        Renvoie la position du joueur (x,y) sur la page par rapport a son coin superieur gauche
        """
        return (self.x, self.y)
    
    def get_center_pos(self):
        """
        Renvoie la position du joueur (x,y) sur la page centree sur le joueur
        """
        x = int(self.x + self.width / 2)
        y = int(self.y + self.height / 2)
        return (x,y)
        
    def render(self):
        """
        Actualise la position du joueur sur la page
        """
        self.helper.change_dimensions(self.id, (self.x, self.y))
        
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
            self.helper.change_image(self.id, ANIM_DEATH)
        return self.dead
    
    def attack(self, enemies: list[Enemy]):
        self.weapon.attack(enemies)
        
    def is_dead(self):
        """
        Renvoie True si le joueur est mort, False sinon
        """
        return self.dead
    
