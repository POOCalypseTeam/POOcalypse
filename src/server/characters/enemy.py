from math import atan2, sin, cos, sqrt
import time
import web_helper

# TODO: Afficher une barre de vie, seulement lorsqu'elle n'est pas pleine
class Enemy:
    def __init__(self, web_helper: web_helper.Helper, position: tuple, img_path: str, health: int):
        self.helper = web_helper
        
        self.x = position[0]
        self.y = position[1]
        
        self.id = self.helper.add_image(img_path, position)
        
        # TODO: Ajouter de la regen
        self.health = health
        self.dead = False
        self.range = 40
        self.last_attack = time.time()
        self.cooldown = 0.7
        self.attack_amount = 1
        
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
        
    def attack(self, player):
        if time.time() - self.last_attack >= self.cooldown:
            player.hit(self.attack_amount)
            self.last_attack = time.time()
            
    def hit(self, damage: int):
        self.health -= damage
        self.health = max(0, self.health)
        if self.health == 0:
            self.helper.remove_html(self.id)
            self.dead = True
            
    def is_dead(self):
        return self.dead

    def update(self, delta_time: float, player):
        # TODO: Reflechir si c'est pas mieux de faire ca dans la boucle principale pour tous les ennemis et appeler les fonction d'attaques de tous les ennemis concernes a la place
        if self.within_range(player.get_center_pos()):
            self.attack(player)
        else:
            self.track_player(player.get_center_pos())
            self.x += self.move[0] * delta_time
            self.y += self.move[1] * delta_time
            self.helper.change_dimensions(self.id, (self.x, self.y))
