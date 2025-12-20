from math import atan2, sin, cos, sqrt
import time
import wsinter

from web.main_web import add_image, change_dimensions
from player import Player

class Enemy:
    def __init__(self, web_manager: wsinter.Inter, position: tuple, img_path: str, health: int):
        self.ws = web_manager
        
        self.x = position[0]
        self.y = position[1]
        
        self.id = add_image(img_path, position)
        
        self.health = health
        self.range = 40
        self.last_attack = time.time()
        self.cooldown = 0.5
        
        self.movement_coef = 15
        self.movement = (0, 0)
        
    def track_player(self, player_position: tuple):
        """
        Cette methode permet de faire aller l'ennemi dans la direion du joueur
        """
        # On calcule l'angle de deplacement
        X = player_position[0]
        Y = player_position[1]
        dX = X - self.x
        dY = Y - self.y
        a = atan2(dY, dX)
        # On ajuste le mouvement de l'ennemi pour aller vers le joueur
        self.move = (cos(a) * self.movement_coef, sin(a) * self.movement_coef)        
        
    def within_range(self, position: tuple):
        distance = (position[0] - self.x) ** 2
        distance += (position[1] - self.y) ** 2
        distance = sqrt(distance)
        return distance <= self.range
        
    def attack(self, player: Player):
        if time.time() - self.last_attack >= self.cooldown:
            player.hit(10)
            self.last_attack = time.time()

    def update(self, delta_time: float, player: Player):
        # TODO: Reflechir si c'est pas mieux de faire ca dans la boucle principale pour tous les ennemis et appeler les fonction d'attaques de tous les ennemis concernes a la place
        if self.within_range(player.get_position()):
            self.attack(player)
        else:
            self.track_player(player.get_position())
            self.x += self.move[0] * delta_time
            self.y += self.move[1] * delta_time
            change_dimensions(self.id, (self.x, self.y))
