import sqlite3
from math import ceil

import web_helper

BOARD_PATH = "content/data/worlds/worlds.db"
TILESET_PATH = "assets/tilesets/%SET%/%IMG%.png"

class Board:
    def __init__(self, helper: web_helper.Helper, world: str, block_size: int = 16, tile_size: int = 32):
        """
        Parametres:
            - helper: L'instance Helper de la librairie web_helper
            
            - world: Le monde a charger
            
            - block_size: La taille en nombre de tiles de chaque bloc, defaut=16
            
            - tile_size: La taille en pixels de chaque tile sur la page, defaut=32
        """
        self.helper = helper
        self.world = world
        self.block_size = block_size
        self.tile_size = tile_size
        
        # Pour chaque couche, on crée un div
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        base.execute("SELECT layer_index FROM layers WHERE world=?;", (self.world,))
        layers = base.fetchall()
        if layers == None:
            raise ValueError("Ce monde n'a pas de couches")
        for layer in layers:
            self.helper.ws.insere("layer_" + str(layer[0]), "div", style={"z-index": layer[0] * 2}, parent="board")
        
    def load(self, layer: int):
        # On suppose que la position de base est 0;0, dont on fait le rendu en haut a gauche
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        # On recupere le dossier des images pour ce layer
        base.execute("SELECT tileset FROM layers WHERE world=? AND layer_index=? LIMIT 1;", (self.world, layer))
        result = base.fetchone()
        if result == None:
            raise ValueError("Cette couche n'existe pas avec ce monde")
        tileset = result[0]
        
        # On récupère la taille de la fenetre
        w,h = self.helper.ws.get_window_size()
        # On calcule le nombre de blocs x et y a aller chercher
        block_pixel_size = self.block_size * self.tile_size
        block_w,block_h = (ceil(w / (block_pixel_size)), ceil(h / block_pixel_size))
        # Pour chaque bloc, on récupère toutes les tiles correspondantes et on en fait le rendu
        for block_x in range(0, block_w):     # Pour l'instant on commence a 0
            for block_y in range(0, block_h): # mais ca depend d'ou etait le joueur avant
                block_offset = (block_x * block_pixel_size, block_y * block_pixel_size)

                # On recupere l'id du block
                base.execute("SELECT block_id FROM blocks WHERE block_x=? AND block_y=? AND world=? AND layer_index=? LIMIT 1;", (block_x, block_y, self.world, layer))
                block_id = base.fetchone()
                if block_id == None:
                    continue
                                
                base.execute("SELECT x,y,image_name FROM tiles WHERE block_id=?;", (block_id[0],))
                tiles = base.fetchall()
                for tile in tiles:
                    img_path = TILESET_PATH.replace("%SET%", tileset).replace("%IMG%", tile[2])
                    position = (block_offset[0] + tile[0] * self.tile_size, block_offset[1] + tile[1] * self.tile_size)
                    self.helper.add_image(img_path, position, (self.tile_size,self.tile_size), parent="layer_" + str(layer))
                
        #for t in board:
        #    img_id = self.helper.add_image(IMG_PATH+t["tile"]+".png",(t["x"]*IMG_SIZE,t["y"]*IMG_SIZE),(IMG_SIZE,IMG_SIZE), None, "div_board"+str(self.layer))
