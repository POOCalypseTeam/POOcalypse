from math import sqrt, atan2, sin, cos
import web_helper

from .weapon import Weapon
from .enemy import Enemy

IMG_PATH = "assets/spritesheets/blonde_man/blonde_man_001.png"
IMG_SIZE = 32
MOVE_AMOUNT = 10
MIN_X = 0
MIN_Y = 0

# Contient le joueur
class Player:
    def __init__(self, helper: web_helper.Helper, position: tuple):
        self.helper = helper
        
        self.x = position[0]
        self.y = position[1]
        # TODO: Resize hitbox to fit character best
        self.width = IMG_SIZE
        self.height = IMG_SIZE
        self.id = "player"
        self.render()
        
        self.health = 5
        self.max_health = 5
        self.dead = False

        self.weapon = Weapon(10, 40, 0.3)
        
        self.movement_vector = [0, 0]
        # Changés par le sol / environnement
        self.max_movement = 1
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
    
    def update(self, delta_time: float, keys: list, enemies: list[Enemy]):
        self.update_movement(delta_time, keys)
        if 'KeyR' in keys:
            self.attack(enemies)
    
    def update_movement(self, delta_time: float, keys: list):
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
        if movement != [0, 0]:
            self.move_range(movement)
        
        if self.movement_vector != [0, 0]:    
            self.move(self.movement_vector)
            self.render()
        
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
    
    def move(self, movement: tuple):
        """
        Effectue le mouvement indique sur le joueur tout en veillant a ce qu'il reste dans les bornes de la fenetre
        
        Parametres:
            - movement: tuple de la forme (x,y) indiquant la quantite de mouvement dans chacune des directions
        """
        window_size = self.helper.ws.get_window_size()
        
        self.x += movement[0]
        self.x = min(self.x, window_size[0] - self.width)
        self.x = max(MIN_X, self.x)
        
        self.y += movement[1]
        self.y = min(self.y, window_size[1] - self.height)
        self.y = max(MIN_Y, self.y)
        
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
        health_width = self.health * 60 / self.max_health
        self.helper.ws.attributs("health", style={"width": f"{health_width}px"})
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
    
