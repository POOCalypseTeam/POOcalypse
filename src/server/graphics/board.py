import sqlite3
import os # listdir
from math import ceil

import web_helper

BOARD_PATH = "content/data/worlds/worlds.db"
TILESET_PATH = "assets/tilesets/%SET%/%IMG%.png"

BLOCKS_SIZE = 16
# La taille d'une tile classique, sans zoom
TRANSLATE_AMOUNT = 16

class Board:
    def __init__(self, helper: web_helper.Helper, world: str, zoom: int = 2):
        """
        Parametres:
            - helper: L'instance Helper de la librairie web_helper
            
            - world: Le monde a charger
            
            - block_size: La taille en nombre de tiles de chaque bloc, defaut=16
            
            - tile_size: La taille en pixels de chaque tile sur la page, defaut=16
        """
        self.helper = helper
        self.world = world
        self.zoom = zoom
        
        self.block_size = BLOCKS_SIZE
        # Ca depend des layers
        self.tile_pixel_sizes = {}
        self.block_pixel_sizes = {}
        self.collisions = {}
        
        self.layers: dict[int, str] = {}
        
        # Coordonnees du centre en pixels
        self.origin = (0, 0)
        
        # On prete attention a la taille de board
        self.board_size = self.update_board_size()
        
        # Pour chaque couche, on crée un div
        # TODO: Utiliser un système asynchrone commun aux plusieurs threads dans lesquels link et base peuvent etre utilises, comme ca il n'y a qu'une seule instance de link (ou un objet resource par exemple)
        self.link = sqlite3.connect(BOARD_PATH, check_same_thread=False)
        self.base = self.link.cursor()
        
        # Ajoute les elements pour ce monde precis
        self.base.execute("SELECT layer_index,tileset,tiles_size,collisions FROM layers WHERE world=? ORDER BY layer_index ASC;", (self.world,))
        layers = self.base.fetchall()
        if layers == None:
            print("Ce monde n'a pas de couche!")
            self.link.close()
            return
        layers = [list(layer) for layer in layers]
        
        for layer in layers:
            # On map les couches avec leur tileset
            self.layers[layer[0]] = layer[1]
            self.tile_pixel_sizes[layer[0]] = layer[2]
            self.block_pixel_sizes[layer[0]] = layer[2] * BLOCKS_SIZE
            self.collisions[layer[0]] = layer[3]
            
            self.helper.ws.insere("layer_" + str(layer[0]), "div", style={"z-index": layer[0] * 2}, parent="tiles")
        
        self.load_all()
        
    def update_board_size(self) -> tuple[float, float]:
        """
        Actualise les dimensions de la fenetre du navigateur pour self.board_size
        
        Renvoie le tuple (w,h) avec les dimensions de la fenetre du navigateur
        """
        size = self.helper.ws.get_window_size()
        # Pour savoir quels coefficients appliquer, se referer a editor.css
        w = size[0]
        h = size[1]
        self.board_size = (w, h)
        return self.board_size
    
    def render_block(self, block_id, layer, block_x, block_y):
        """
        Affiche toutes les tiles comprises dans un bloc
        
        Le seul appel au SGBD est pour recuperer toutes les tiles du bloc, non pour recuperer sa couche ou sa position
        
        Parametres:
            - block_id: L'id du bloc dans le SGBD
            
            - layer: Couche du bloc dans le monde
            
            - block_x,block_y: Position du bloc dans le monde
        """        
        block_offset = ((block_x) * self.block_pixel_sizes[layer], (block_y) * self.block_pixel_sizes[layer])
        self.base.execute("SELECT x,y,image_name FROM tiles WHERE block_id=?;", (block_id,))
        tiles = self.base.fetchall()
        for tile in tiles:
            img_id = "_".join(map(str, [layer, block_x * self.block_size + tile[0], block_y * self.block_size + tile[1]]))
            img_path = TILESET_PATH.replace("%SET%", self.layers[layer]).replace("%IMG%", tile[2])
            position = (self.zoom * (block_offset[0] + tile[0] * self.tile_pixel_sizes[layer]), self.zoom * (block_offset[1] + tile[1] * self.tile_pixel_sizes[layer]))
            self.helper.add_image_id(img_id, img_path, position, (self.zoom * self.tile_pixel_sizes[layer], self.zoom * self.tile_pixel_sizes[layer]), parent=block_id)
    
    def add_block(self, layer, block_x, block_y) -> int:
        """
        Ajoute un div sur la page HTML pour le bloc

        Si le bloc n'existe pas dans la base de données, il n'est pas cree !
        
        Parametres:
            - layer: Couche du bloc
            
            - block_x,block_y: Position du bloc
            
        Les parametres permettent de determiner le block_id
        
        Renvoie le block_id
        """
        self.base.execute("SELECT block_id FROM blocks WHERE block_x=? AND block_y=? AND world=? AND layer_index=? LIMIT 1;", (block_x, block_y, self.world, layer))
        block = self.base.fetchone()
        if block == None:
            return
        
        block_id = block[0]
        self.helper.ws.insere(block_id, "div", parent="layer_" + str(layer))
        self.render_block(block_id, layer, block_x, block_y)
        
        return block_id


    def load(self, layer: int, center_block: tuple = (0, 0)):
        """
        Charge le layer specifie sur la page en centrant sur le block donne 
        """
        # On récupère la taille de la fenetre
        w,h = self.board_size
        # TODO: Considerer le zoom pour savoir combien en mettre dans cette zone ?
        block_w,block_h = (ceil(w / (self.block_pixel_sizes[layer])), ceil(h / self.block_pixel_sizes[layer]))
        block_w_offset = block_w // 2 + 1
        block_h_offset = block_h // 2 + 1
        
        x_start = center_block[0] - block_w_offset
        x_end = center_block[0] + block_w_offset
        y_start = center_block[1] - block_h_offset
        y_end = center_block[1] + block_h_offset
        
        for block_x in range(x_start, x_end):
            for block_y in range(y_start, y_end):
                self.add_block(layer, block_x, block_y)

    def load_all(self):
        """
        Charge toute la carte specifiee sur la page en centrant au coordonnees donnees
        """
        w,h = self.update_board_size()
        self.helper.ws.attributs("tiles", style={"left": str(-(self.origin[0]) + w / 2) + "px", "top": str(-(self.origin[1]) + h / 2) + "px"})
        for layer in self.layers.keys():
            self.load(layer, (0, 0))

    def translate(self, move: tuple):
        """
        Bouge la carte en utilisant le vecteur move, on bouge en utilisant le nombre de pixels dans move
        """
        if move == [0, 0]:
            return
        ox,oy = self.origin
        mx = move[0] * self.zoom
        my = move[1] * self.zoom
        
        self.origin = (ox + mx, oy + my)
        
        w,h = self.update_board_size()
        
        
        
        self.helper.ws.attributs("tiles", style={"left": str(-(self.origin[0]) + w / 2) + "px", "top": str(-(self.origin[1]) + h / 2) + "px"})

    
class EditorBoard(Board):
    def __init__(self, helper: web_helper.Helper, world: str):
        super().__init__(helper, world)
        layers = []
        for l in self.layers.keys():
            layers.append([l, self.layers[l], self.tile_pixel_sizes[l], self.collisions[l]])
        self.helper.ws.injecte("addLayers(" + str(layers) + ")")

        self.layer: int = 0
        self.tile: str = ""
        self.tool: str = "draw"
        
        # Coordonnees pour la selection, un tuple lorsque actif et None lorsque rien (bien vu l'artiste)
        self.p1: tuple[tuple[int, int], tuple[int, int]] = None
        self.p2: tuple[tuple[int, int], tuple[int, int]] = None

        # Utilises pour action, qui devrait sinon en initialiser beaucoup trop
        self.link = sqlite3.connect(BOARD_PATH, check_same_thread=False)
        self.base = self.link.cursor()
        self.commit = False
        
        w,h = self.board_size
        self.helper.ws.attributs("board", style={"background-position-x": str(-(self.origin[0]) + w / 2) + "px"\
                                                ,"background-position-y": str(-(self.origin[1]) + h / 2) + "px"})
        
    def update_board_size(self) -> tuple[float, float]:
        size = self.helper.ws.get_window_size()
        # Pour savoir quels coefficients appliquer, se referer a editor.css
        w = size[0] * 0.8
        h = size[1] * 0.85
        self.board_size = (w, h)
        return self.board_size
        
    # Methodes pour l'interaction PAGE -> BOARD
    
    def layer_changed(self, _, o: int):
        self.layer = int(o)
        
        # On supprime tout d'abord
        self.helper.ws.remove_children("tileset")
        
        tileset_path = "/assets/tilesets/" + self.layers[self.layer] + "/"
        # Charge les images
        i = 0
        for file in os.listdir("content" + tileset_path):
            self.helper.ws.insere("palette_" + str(i), "img", attr={'src':'../' + tileset_path + file}, parent="tileset")
            i += 1
            
        self.helper.ws.injecte("addTilesEvent();")
        
    def tile_changed(self, _, o):
        self.tile = o
        if self.tool == "select" and self.p1 != None and self.p2 != None:
            self.selection(self.tile)
        
    def create_layer(self, _, o: list[str, str, str, str]):
        self.layers[int(o[0])] = o[1]
        self.tile_pixel_sizes[int(o[0])] = int(o[2])
        self.block_pixel_sizes[int(o[0])] = int(o[2]) * BLOCKS_SIZE
        
        self.base.execute("INSERT INTO layers VALUES (?,?,?,?,?);", (self.world, int(o[0]), o[1], int(o[2]), bool(o[3])))
        self.link.commit()
        
        self.helper.ws.insere("layer_" + o[0], "div", style={"z-index": int(o[0]) * 2}, parent="tiles")
        
    def delete_layer(self, _, o):
        if self.layer != int(o):
            raise ValueError("Il y a un probleme de synchronisation entre le client et le serveur, relancez.")
        
        self.helper.ws.remove("layer_option_" + str(self.layer))
        self.helper.ws.remove("layer_" + str(self.layer))
        del self.layers[self.layer]
        del self.tile_pixel_sizes[self.layer]
        del self.block_pixel_sizes[self.layer]
        
        self.base.execute("DELETE FROM layers WHERE world=? AND layer_index=?;", (self.world, self.layer))
        self.link.commit()
        
    def tool_changed(self, _m, o):
        """
        Cette méthode est appelée lorsque l'outil est changé, via un gestionnaire d'événements WsInter
        
        Lorsque l'outil de sélection était sélectionné et que la gomme vient d'être cliquée
        """
        if self.tool == "select" and o == "erase" and self.p1 != None and self.p2 != None:
            self.selection("__erase__")
            return
        self.tool = o
        # Permet de reset la selection, par exemple en appuyant a nouveau sur le bouton de selection
        self.p1 = None
        self.p2 = None
        self.helper.ws.add_class("corner-1", "hidden")
        self.helper.ws.add_class("corner-2", "hidden")
        
    def translate(self, move: tuple):
        super().translate(move)
        
        w,h = self.board_size
        self.helper.ws.attributs("board", style={"background-position-x": str(-(self.origin[0]) + w / 2) + "px"\
                                                ,"background-position-y": str(-(self.origin[1]) + h / 2) + "px"})
        
    def translate_direction(self, move: tuple):
        """
        Bouge la carte en utilisant les directions donnees par le vecteur move, on bouge en utilisant TRANSLATE_AMOUNT
        """
        if move == [0, 0]:
            return
        self.translate((move[0] * TRANSLATE_AMOUNT, move[1] * TRANSLATE_AMOUNT))

    def get_block_id(self, block_x: int, block_y: int, create: bool = False) -> str:
        """
        Renvoie l'id du bloc dans la base de donnees et le cree si create est a True
        
        S'il n'y a pas de tel bloc, renvoie None.
        
        Parametres:
            - (block_x, block_y): Les coordonnees du bloc
            
            - create: True si bloc doit etre cree lorsqu'il n'existe pas, False sinon
        """
        self.base.execute("SELECT block_id FROM blocks WHERE world=? AND layer_index=? AND block_x=? AND block_y=?;", (self.world, self.layer, block_x, block_y))
        res = self.base.fetchall()
        block_id = None
        if len(res) > 1:
            raise ValueError("Plusieurs blocs existent")
        elif len(res) == 0:
            if create:
                # On cree un nouveau bloc
                self.base.execute("INSERT INTO blocks(world,layer_index,block_x,block_y) VALUES (?,?,?,?);", (self.world, self.layer, block_x, block_y))
                self.base.execute("SELECT block_id FROM blocks WHERE world=? AND layer_index=? AND block_x=? AND block_y=?;", (self.world, self.layer, block_x, block_y))
                block_id = self.base.fetchone()[0]
                self.helper.ws.insere(block_id, "div", parent="layer_" + str(self.layer))
        else:
            block_id = res[0][0]
            
        return block_id
    
    def add_or_edit_tile(self, block_id: str, block_pos: tuple, block_offsets: tuple, tile_pos: tuple) -> None:
        """
        Ajoute ou modifie une tile a la position donnee
        
        La tile utilisee pour dessiner est celle contenue dans self.tile[:-4]
        
        Parametres:
            - block_id: L'id du bloc dans lequel est la tile, on suppose qu'il existe dans la base de donnee
            
            - block_pos: Les coordonnees (x,y) du bloc
            
            - block_offsets: Les decalages (w,h) en pixels pour le bloc
            
            - tile_pos: Les coordonnees de la tile dans le bloc
        """
        self.base.execute("SELECT COUNT(image_name) FROM tiles WHERE block_id=? AND x=? AND y=?;", (block_id, tile_pos[0], tile_pos[1]))
        res = self.base.fetchall()[0][0]
        img_id = "_".join(map(str, [self.layer, block_pos[0] * self.block_size + tile_pos[0], block_pos[1] * self.block_size + tile_pos[1]]))
        if res > 1:
            raise ValueError("Plusieurs tiles existent")
        elif res == 0:
            # On cree une nouvelle tile
            self.base.execute("INSERT INTO tiles VALUES (?,?,?,?);", (block_id, tile_pos[0], tile_pos[1], self.tile[:-4]))
            position = (self.zoom * (tile_pos[0] * self.tile_pixel_sizes[self.layer]) + block_offsets[0], self.zoom * (tile_pos[1] * self.tile_pixel_sizes[self.layer]) + block_offsets[1])
            path = TILESET_PATH.replace("%SET%", self.layers[self.layer]).replace("%IMG%", self.tile[:-4])
            self.helper.add_image_id(img_id, path, position, (self.zoom * self.tile_pixel_sizes[self.layer], self.zoom * self.tile_pixel_sizes[self.layer]), parent=block_id)
        else:
            # On modifie la tile d'avant
            self.helper.ws.attributs(img_id, attr={'src': "../" + TILESET_PATH.replace("%SET%", self.layers[self.layer]).replace("%IMG%", self.tile[:-4])})
            self.base.execute("UPDATE tiles SET image_name = ? WHERE block_id=? AND x=? AND y=?;", (self.tile[:-4], block_id, tile_pos[0], tile_pos[1]))
    
    def adjust_selection(self):
        """
        Renvoie un tuple (c1, c2) avec c1 et c2 respectivement les coins haut-gauche et bas-droit, peu importe self.p1 et self.p2
        """

        x1 = self.p1[0][0] * self.block_size + self.p1[1][0]
        y1 = self.p1[0][1] * self.block_size + self.p1[1][1]
        
        x2 = self.p2[0][0] * self.block_size + self.p2[1][0]
        y2 = self.p2[0][1] * self.block_size + self.p2[1][1]

        if x1 < x2:
            min_x = (self.p1[0][0], self.p1[1][0])
            max_x = (self.p2[0][0], self.p2[1][0])
        else:
            min_x = (self.p2[0][0], self.p2[1][0])
            max_x = (self.p1[0][0], self.p1[1][0])

        if y1 < y2:
            min_y = (self.p1[0][1], self.p1[1][1])
            max_y = (self.p2[0][1], self.p2[1][1])
        else:
            min_y = (self.p2[0][1], self.p2[1][1])
            max_y = (self.p1[0][1], self.p1[1][1])
            
        c1 = ((min_x[0], min_y[0]), (min_x[1], min_y[1]))
        c2 = ((max_x[0], max_y[0]), (max_x[1], max_y[1]))
        
        return (c1, c2)
    
    def selection(self, tile: str):
        """
        Fait une action sur la zone selectionnee
        
        Parametres:
            - tile: Une chaine de caracteres qui represente soit une tile, soit __erase__ et qui sert a effacer toute la zone
        """
        assert self.p1 != None and self.p2 != None, "La selection n'est pas complete"
        
        corner1, corner2 = self.adjust_selection()
        
        create = tile != "__erase__"
        
        tile_x = corner1[1][0]
        tile_y = corner1[1][1]
        
        block_x = corner1[0][0]
        block_y = corner1[0][1]
        current_block_id = self.get_block_id(block_x, block_y, create=True)
        
        x_count = (corner2[0][0] * self.block_size + corner2[1][0]) - (corner1[0][0] * self.block_size + corner1[1][0])
        y_count = (corner2[0][1] * self.block_size + corner2[1][1]) - (corner1[0][1] * self.block_size + corner1[1][1])

        block_offset_x = block_x * self.block_pixel_sizes[self.layer] * self.zoom
        block_offset_y = block_y * self.block_pixel_sizes[self.layer] * self.zoom
        
        for _ in range(x_count + 1):
            
            for _ in range(y_count + 1):
                if current_block_id == None:
                    continue
                
                img_id = "_".join(map(str, [self.layer, block_x * self.block_size + tile_x, block_y * self.block_size + tile_y]))
                if tile == "__erase__":
                    self.helper.ws.remove(img_id)
                    self.base.execute("DELETE FROM tiles WHERE block_id=(SELECT block_id FROM blocks WHERE world=? AND layer_index=? AND block_x=? AND block_y=?) AND x=? AND y=?;", (self.world, self.layer, block_x, block_y, tile_x, tile_y))
                else: 
                    self.add_or_edit_tile(current_block_id, (block_x, block_y), (block_offset_x, block_offset_y), (tile_x, tile_y))
                
                tile_y += 1
                if tile_y == self.block_size:
                    block_y += 1
                    current_block_id = self.get_block_id(block_x, block_y, create=create)
                    block_offset_x = block_x * self.block_pixel_sizes[self.layer] * self.zoom
                    block_offset_y = block_y * self.block_pixel_sizes[self.layer] * self.zoom
                    tile_y = 0
            
            tile_x += 1
            if tile_x == self.block_size:
                block_x += 1
                tile_x = 0
            tile_y = corner1[1][1]
            block_y = corner1[0][1]
            current_block_id = self.get_block_id(block_x, block_y, create=create)
            block_offset_x = block_x * self.block_pixel_sizes[self.layer] * self.zoom
            block_offset_y = block_y * self.block_pixel_sizes[self.layer] * self.zoom

    def action(self, button: str, click_pos: tuple):
        """
        Lorsqu'un bouton de la souris est appuye sur board
        
        Parametres:
            - button: Le bouton qui a ete appuye, parmi ['L', 'R', 'M'] respectivement pour Gauche, Droite et Milieu
            
            - click_pos: La position en pixels sur la page du clic
        """
        def add_tile(block_pos, block_offsets, tile_pos):
            """
            Cette methode ajoute une tile a la position donnee sur la page et actualise la base de donnees, elle ajoute un bloc si necessaire
            """
            block_id = self.get_block_id(block_pos[0], block_pos[1], create=True)
            self.add_or_edit_tile(block_id, block_pos, block_offsets, tile_pos)
                        
        def remove_tile(block_pos, tile_pos):
            """
            Cette methode supprime la tile specifiee de la page et actualise la base de donnees
            """
            block_id = self.get_block_id(block_pos[0], block_pos[1])
            
            self.base.execute("SELECT COUNT(image_name) FROM tiles WHERE block_id=? AND x=? AND y=?;", (block_id, tile_pos[0], tile_pos[1]))
            res = self.base.fetchall()[0][0]
            img_id = "_".join(map(str, [self.layer, block_pos[0] * self.block_size + tile_pos[0], block_pos[1] * self.block_size + tile_pos[1]]))
            if res > 1:
                raise ValueError("Pas normal du tout")
            elif res == 0:
                return
        
            # On modifie la tile d'avant
            self.helper.ws.remove(img_id)
            self.base.execute("DELETE FROM tiles WHERE block_id=? AND x=? AND y=?;", (block_id, tile_pos[0], tile_pos[1]))


        if self.link == None:
            self.link = sqlite3.connect(BOARD_PATH)
            self.commit = True
            try:
                self.link.autocommit = True
            except AttributeError:
                print("L'attribut autocommit n'est pas disponible pour sqlite3")
                self.commit = False
            self.base = self.link.cursor()
        
        w,h = self.update_board_size()
        
        x,y = click_pos[0] - int(w // 2) + self.origin[0], click_pos[1] - int(h // 2) + self.origin[1]
        
        block_x = (x) // (self.block_pixel_sizes[self.layer] * self.zoom)
        block_y = (y) // (self.block_pixel_sizes[self.layer] * self.zoom)
        
        block_offset_x = block_x * self.block_pixel_sizes[self.layer] * self.zoom
        block_offset_y = block_y * self.block_pixel_sizes[self.layer] * self.zoom
        
        tile_x = (x - block_offset_x) // (self.tile_pixel_sizes[self.layer] * self.zoom)
        tile_y = (y - block_offset_y) // (self.tile_pixel_sizes[self.layer] * self.zoom)
        
        match self.tool:
            case 'draw':
                if button == 'L' and self.tile != "":
                    add_tile((block_x, block_y), (block_offset_x, block_offset_y), (tile_x, tile_y))
                elif button == 'R':
                    remove_tile((block_x, block_y), (tile_x, tile_y))
            case 'erase':
                remove_tile((block_x, block_y), (tile_x, tile_y))
            case 'select':
                # Une fois qu'une zone est selectionnee, il suffit d'appuyer sur la gomme ou une tile afin que toute la zone soit affectee par soit la gomme soit une tile
                pos = ((block_x, block_y), (tile_x, tile_y))
                page_pos = (self.zoom * (tile_x * self.tile_pixel_sizes[self.layer]) + block_offset_x, self.zoom * (tile_y * self.tile_pixel_sizes[self.layer]) + block_offset_y)
                if button == 'L':
                    self.p1 = pos
                    self.helper.ws.remove_class("corner-1", "hidden")
                    self.helper.ws.attributs("corner-1", style={"left": str(page_pos[0]) + "px", "top": str(page_pos[1]) + "px"})
                if button == "R":
                    self.p2 = pos
                    self.helper.ws.remove_class("corner-2", "hidden")
                    self.helper.ws.attributs("corner-2", style={"left": str(page_pos[0]) + "px", "top": str(page_pos[1]) + "px"})
            case _:
                raise TypeError("Il n'existe pas d'outil de ce type")
