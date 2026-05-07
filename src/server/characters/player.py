from math import sqrt, atan2, sin, cos
import time
import web_helper
from constants import PLAYER_SPRITESHEET_PATH

from .weapon import Weapon
from .enemy import Enemy


ANIM_STOP           = PLAYER_SPRITESHEET_PATH + 'player_stop.gif'
ANIM_LEFT           = PLAYER_SPRITESHEET_PATH + 'player_left.gif'
ANIM_BOTTOM         = PLAYER_SPRITESHEET_PATH + 'player_bottom.gif'
ANIM_RIGHT          = PLAYER_SPRITESHEET_PATH + 'player_right.gif'
ANIM_TOP            = PLAYER_SPRITESHEET_PATH + 'player_top.gif'
ANIM_DEATH          = PLAYER_SPRITESHEET_PATH + 'player_death.gif'
ANIM_ATTACK_TOP     = PLAYER_SPRITESHEET_PATH + 'player_attack_top.gif'
ANIM_ATTACK_BOTTOM  = PLAYER_SPRITESHEET_PATH + 'player_attack_bottom.gif'
ANIM_ATTACK_RIGHT   = PLAYER_SPRITESHEET_PATH + 'player_attack_right.gif'
ANIM_ATTACK_LEFT    = PLAYER_SPRITESHEET_PATH + 'player_attack_left.gif'

IMG_SIZE = 64
MOVE_AMOUNT = 50
MIN_X = 0
MIN_Y = 0
ANIM_ATTACK_DURATION = 0.450    # 0.550
ANIM_DEATH_DURATION = 0.450     # Dans les faits cette valeur est égale à : 0.650
                                # Mais comme les updates ne se font pas toutes les nanosecondes, on pourrait dépasser ce temps et l'animation bouclerait, comme un glitch
                                # Pour éviter cela, on place la fin de l'animation au tout début de la dernière frame

# Contient le joueur
class Player:
    def __init__(self, helper: web_helper.Helper, position: tuple):
        self.helper = helper
        self.x = position[0]
        self.y = position[1]
        self.width = IMG_SIZE
        self.height = IMG_SIZE
        self.id = self.helper.add_image(ANIM_STOP, (self.x, self.y), size=(64, 64), parent="player")
        self.att = False
        self.delta_sum = 0
        self.current_anim = ANIM_STOP
        
        self.health = 5
        self.max_health = 5
        self.last_heal = time.time()
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
        if self.dead:
            if ANIM_DEATH_DURATION - self.delta_sum > 0.017: # Le temps d'une frame
                self.delta_sum += delta_time
            return [0,0]
        
        if 'KeyR' in keys:
            self.attack(enemies)
            self.att = True
            self.delta_sum = 0
            
        if ANIM_ATTACK_DURATION - self.delta_sum > 0.017:
            self.delta_sum += delta_time
        else:
            self.att = False

        if 'KeyH' in keys:
            self.heal(1)
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
        new_anim = None
        if movement != [0, 0]:
            self.move_range(movement)        
            if movement[0] > 0:
                new_anim = ANIM_ATTACK_RIGHT if self.att else ANIM_RIGHT
            elif movement[0] < 0:
                new_anim = ANIM_ATTACK_LEFT if self.att else ANIM_LEFT
            elif movement[1] > 0 :
                new_anim = ANIM_ATTACK_BOTTOM if self.att else ANIM_BOTTOM
            elif movement[1] < 0:
                new_anim = ANIM_ATTACK_TOP if self.att else ANIM_TOP
        else:
            new_anim = ANIM_ATTACK_BOTTOM if self.att else ANIM_STOP
        
        # On évite de changer trop les images, surtout pour les GIFs
        if new_anim != self.current_anim:
            self.current_anim = new_anim
            self.helper.change_image(self.id, self.current_anim, self.att)

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
        
    def hit(self, damage: int):
        """
        Fait des degats au joueur
        
        Parametres:
            - damage: un entier donnant le nombre de PV que l'attaque doit infliger
        
        Renvoie True si le joueur est mort, False sinon
        """
        assert type(damage) == int, "Le nombre de dégats donné n'est pas entier"
        for i in range(min(5, damage)):
            self.helper.ws.add_class("heart"+str(self.health - i), "hit")
        self.health = max(0, self.health - damage)
        if not self.dead and self.health == 0:
            self.dead = True
            self.delta_sum = 0
            self.helper.change_image(self.id, ANIM_DEATH, True)
        return self.dead
    
    def heal(self, cooldown: float):
        if time.time() - self.last_heal >= cooldown:
            self.health = min(self.health + 1, self.max_health)
            self.helper.ws.remove_class("heart" + str(self.health), "hit")
            self.last_heal = time.time()

    def attack(self, enemies: list[Enemy]):
        self.weapon.attack(enemies)
        
    def is_dead(self):
        """
        Renvoie True si le joueur est mort, False sinon
        """
        return self.dead

        