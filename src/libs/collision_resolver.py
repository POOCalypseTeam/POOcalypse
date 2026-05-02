from constants import BLOCKS_SIZE

# ==== Tags ==== #
CANT_PASS    = 1       # Impossible de passer a travers
TRIGGER      = 2       # Déclenche un événement au passage
MOVABLE      = 4       # Possible de bouger le collider (ex: joueur, ennemis)
BLOCK        = 8       # Bloc qui contient des collisions mais pas sur toute sa surface, il sera divisé en 4 blocs égaux jusq'une tile
TARGET       = 16      # Collider qui peut être visé par un projectile
INTERACTABLE = 32      # Il est possible d'intéragir en appuyant sur E


class Collider:
    def __init__(self, position: tuple[float, float, float, float], tag_code: int, handler: callable = None):
        """
        Parametres:
            - position: Position sur la carte, sous la forme de tuple (X1, Y1, X2, Y2)

            - tag_code: entier décrivant le comportement du collider

            - handler: fonction a appeler si le tag_code contient TRIGGER

        Leve une erreur lorsque le tag_code a TRIGGER mais qu'il n'y a pas de handler, ou l'inverse
        """
        self.position: tuple[float, float, float, float] = position
        self.tag_code: int = tag_code
        self.handler: callable = handler
        if tag_code & TRIGGER and (handler == None or type(handler) != callable):
            raise ValueError("Le code est TRIGGER mais il n'y a pas de handler")
        if (handler != None and type(handler) == callable) and not tag_code & TRIGGER:
            raise ValueError("Il y a un handler mais le code n'est pas TRIGGER")
        
        self.id: int = -1
        
    def get_position_after_movement(self, mov: tuple[float, float]) -> tuple[float, float, float, float]:
        pos = self.position
        return (pos[0] + mov[0], pos[1] + mov[1], pos[2] + mov[0], pos[3] + mov[1])
        
    def check_for_collision(self, box: tuple[float, float, float, float]) -> bool:
        """
        Vérifie s'il y a ou non une collision entre le collider et la boite donnee en parametres
        
        Pour se faire, la méthode parcourt chacun des 4 coins de la boite et regarde si au moins l'un deux est dans le collider auquel cas il y a collision
        
        Parametres:
            - box: Un tuple de 4 flottants représentant les coordonnées de la boite : (X1, Y1, X2, Y2)
            
        Renvoie True s'il y a collision, False sinon
        """
        points = [(box[0], box[1]), (box[0], box[3]), (box[2], box[1]), (box[2], box[3])]
        for point in points:
            if self.position[0] <= point[0] <= self.position[2] and self.position[1] <= point[1] <= self.position[3]:
                return True
        return False
        
    def get_id(self):
        return self.id
    
    def set_id(self, id: int):
        self.id = id

    def is_cant_pass(self):
        return self.tag_code & CANT_PASS
    
    def is_trigger(self):
        return self.tag_code & TRIGGER
    
    def is_movable(self):
        return self.tag_code & MOVABLE
    
    def is_block(self):
        return self.tag_code & BLOCK
    
    def is_target(self):
        return self.tag_code & TARGET

class Block(Collider):
    def __init__(self, position: tuple[float, float, float, float], lods, size: int):
        """
        Parametres:
            - position: Un tuple (X1, Y1, X2, Y2) donnant la position du coin haut gauche du block
            
            - lods: Niveaux de détails conercant les collisions, se référer à board.py.Board.get_block_lods()
            
            - size: Un entier donnant la taille du block en nombre de tiles
        """
        super().__init__(position, BLOCK, handler=None)
        self.size = size
        # Les blocs initalisés ici ne sont pas associés à un id
        size //= 2
        pixel_size = position[2] - position[0]
        center_x = position[2] - (pixel_size / 2) - 1
        center_y = position[3] - (pixel_size / 2) - 1
        # Coins par rapport au pavé numérique du clavier
        self.b7 = None
        self.b9 = None
        self.b1 = None
        self.b3 = None
        if size != 1:
            if lods[1][0]:
                self.b7 = Block((position[0], position[1], center_x, center_y), lods[1], size)
            if lods[2][0]:
                self.b9 = Block((center_x, position[1], position[2], center_y), lods[2], size)
            if lods[3][0]:
                self.b1 = Block((position[0], center_y, center_x, position[3]), lods[3], size)
            if lods[4][0]:
                self.b3 = Block((center_x, center_y, position[2], position[3]), lods[4], size)
        else:
            if lods[1][0]:
                self.b7 = Collider((position[0], position[1], center_x, center_y), CANT_PASS)
            if lods[2][0]:
                self.b9 = Collider((center_x, position[1], position[2], center_y), CANT_PASS)
            if lods[3][0]:
                self.b1 = Collider((position[0], center_y, center_x, position[3]), CANT_PASS)
            if lods[4][0]:
                self.b3 = Collider((center_x, center_y, position[2], position[3]), CANT_PASS)
            
    def check_for_collision(self, box: tuple[float, float, float, float]) -> bool:
        """
        Le but est d'avoir une approche diviser pour régner, le bloc actuel est déjà divisé en 4 plus petits blocs, il reste à savoir quel(s) bloc(s) est/sont concerné(s)
        
        Preuve de la terminaison: les éléments b[1;3;7;9] ont tous l'attribut size divisé par 2, jusqu'à 1, car quotient de la division euclidienne par 2
        
        Lorsque size atteint effectivement 1, ce n'est plus un Block mais un Collider donc il n'y a plus d'appels récursifs, la méthode termine
        """
        # On regarde tout d'abord s'il y a collision avec le gros bloc
        if super().check_for_collision(box):
            # Si oui, on regarde quel petit bloc est concerné et on lui passe l'appel de fonction
            return  (self.b1 != None and self.b1.check_for_collision(box)) or \
                    (self.b3 != None and self.b3.check_for_collision(box)) or \
                    (self.b7 != None and self.b7.check_for_collision(box)) or \
                    (self.b9 != None and self.b9.check_for_collision(box))
        return False
        
        
class CollisionResolver:
    """
    Cette classe permet de répertorier toutes les collisions du jeu, avec différentes couches et différentes actions lorsqu'il y a en effet collision
    """
    
    def __init__(self):
        self.colliders: list[Collider] = []
        self.to_check: list[Collider] = []
    
    def add_collider(self, position: tuple[float, float, float, float], tag_code: int, handler: callable = None) -> None:
        """
        Permet d'ajouter un rectangle qui fait office de collider

        Parametres:
            - position: Position sur la carte, sous la forme de tuple (X1, Y1, X2, Y2)

            - tag_code: entier décrivant le comportement du collider

            - handler: fonction a appeler si le tag_code contient TRIGGER

        Leve une erreur lorsque le tag_code a TRIGGER mais qu'il n'y a pas de handler, ou l'inverse
        
        Renvoie le collider nouvellement créé
        """
        collider = Collider(position, tag_code, handler)
        collider.set_id(len(self.colliders))
        self.colliders.append(collider)
        return collider
    
    def add_block(self, position: tuple[float, float, float, float], block_lods):
        """
        Ajoute un bloc a la liste des colliders
        
        Parametres:
            - position: Position sur la carte du bloc, sous la forme d'un tuple (X1, Y1, X2, Y2)
            
        Renvoie le bloc
        """
        # Le bloc n'a pas de tile pouvant faire une collision, rien ne sert de collide il faut optimiser
        if not block_lods[0]:
            return
        block = Block(position, block_lods, BLOCKS_SIZE)
        block.set_id(len(self.colliders))
        self.colliders.append(block)
        return block
    
    def remove_collider(self, collider):
        """
        Enleve ce collider de la liste des collider
        """
        assert collider.id != -1
        # TODO: ATTENTION, ça peut grandir très vite ça si on ne supprime pas vraiment les colliders
        self.colliders[collider.id] = None

    def attempt_movement(self, pos, mov):
        """
        Appelée par la boucle principale

        Vérifie pour chaque mouvement de la liste s'il est valide ou non et s'il faut déclencher des événements
        """
        validate = True
        nearby = []
        for collision_candidate in self.colliders:
            # On regarde s'il y a collision avec la map
            if validate and collision_candidate.is_block() and collision_candidate.check_for_collision((pos[0] + mov[0], pos[1] + mov[1], pos[2] + mov[0], pos[3] + mov[1])):
                # Si tel est le cas, on renvoie False pour la validation du mouvement
                validate = False
        return (validate, nearby)
