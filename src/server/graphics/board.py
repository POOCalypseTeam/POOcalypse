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
        
        # {layer: (x_start, x_end, y_start, y_end)}
        self.board_bounds: dict[int, tuple[int, int, int, int]] = {}
        # {block_id: (layer, block_x, block_y)}
        self.rendered_blocks: dict[int, tuple[int, int, int]] = {}
        
        self.layers: dict[int, str] = {}
        
        # Centre
        self.origin = (0, 0)
        
        # On prete attention a la taille de board
        self.board_size = self.update_board_size()
        
        # Pour chaque couche, on crée un div
        # TODO: Utiliser un système asynchrone commun aux plusieurs threads dans lesquels link et base peuvent etre utilises, comme ca il n'y a qu'une seule instance de link (ou un objet resource par exemple)
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        # Ajoute les elements pour ce monde precis
        base.execute("SELECT layer_index,tileset,tiles_size,collisions FROM layers WHERE world=? ORDER BY layer_index ASC;", (self.world,))
        layers = base.fetchall()
        if layers == None:
            print("Ce monde n'a pas de couche!")
            link.close()
            return
        layers = [list(layer) for layer in layers]
        
        for layer in layers:
            # On map les couches avec leur tileset
            self.layers[layer[0]] = layer[1]
            self.tile_pixel_sizes[layer[0]] = layer[2]
            self.block_pixel_sizes[layer[0]] = layer[2] * BLOCKS_SIZE
            self.collisions[layer[0]] = layer[3]
            
            self.helper.ws.insere("layer_" + str(layer[0]), "div", style={"z-index": layer[0] * 2}, parent="tiles")
        
        link.close()
        self.load_all()
        
    def update_board_size(self) -> tuple[float, float]:
        size = self.helper.ws.get_window_size()
        # Pour savoir quels coefficients appliquer, se referer a editor.css
        w = size[0]
        h = size[1]
        self.board_size = (w, h)
        return self.board_size
    
    def render_block(self, block_id, layer, block_x, block_y):
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        block_offset = ((block_x) * self.block_pixel_sizes[layer], (block_y) * self.block_pixel_sizes[layer])
        base.execute("SELECT x,y,image_name FROM tiles WHERE block_id=?;", (block_id,))
        tiles = base.fetchall()
        for tile in tiles:
            img_id = "_".join(map(str, [layer, block_x * self.block_size + tile[0], block_y * self.block_size + tile[1]]))
            img_path = TILESET_PATH.replace("%SET%", self.layers[layer]).replace("%IMG%", tile[2])
            position = (self.zoom * (block_offset[0] + tile[0] * self.tile_pixel_sizes[layer]), self.zoom * (block_offset[1] + tile[1] * self.tile_pixel_sizes[layer]))
            self.helper.add_image_id(img_id, img_path, position, (self.zoom * self.tile_pixel_sizes[layer], self.zoom * self.tile_pixel_sizes[layer]), parent=block_id)
    
    def add_block(self, layer, block_x, block_y) -> int:
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        base.execute("SELECT block_id FROM blocks WHERE block_x=? AND block_y=? AND world=? AND layer_index=? LIMIT 1;", (block_x, block_y, self.world, layer))
        block = base.fetchone()
        if block == None:
            return
        
        link.close()
        
        block_id = block[0]
        if block_id in self.rendered_blocks.keys():
            return
        
        self.rendered_blocks[block_id] = (layer, block_x, block_y)
        self.helper.ws.insere(block_id, "div", parent="layer_" + str(layer))
        
        self.render_block(block_id, layer, block_x, block_y)
        
        return block_id


    def load(self, layer: int, center_block: tuple = (0, 0)):
        """
        Charge le layer specifie sur la page en centrant sur le block donne 
        """
        # On récupère la taille de la fenetre
        w,h = self.update_board_size()
        block_w,block_h = (ceil(w / (self.block_pixel_sizes[layer])), ceil(h / self.block_pixel_sizes[layer]))
        block_w_offset = block_w // 2
        block_h_offset = block_h // 2
        
        x_start = center_block[0] - block_w_offset
        x_end = center_block[0] + block_w_offset
        y_start = center_block[1] - block_h_offset
        y_end = center_block[1] + block_h_offset
        self.board_bounds[layer] = (x_start, x_end, y_start, y_end)
        
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
        mx,my = move
        
        self.origin = (ox + mx, oy + my)

        w,h = self.update_board_size()
        
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        blocks_to_remove = dict(self.rendered_blocks)
        
        for layer in self.layers.keys():
            center_block = (int(self.origin[0]) // self.block_pixel_sizes[layer], int(self.origin[1]) // self.block_pixel_sizes[layer])
            
            block_w,block_h = (ceil(w / (self.block_pixel_sizes[layer])), ceil(h / self.block_pixel_sizes[layer]))
            block_w_offset = block_w // 2
            block_h_offset = block_h // 2
            
            x_start = center_block[0] - block_w_offset
            x_end = center_block[0] + block_w_offset
            y_start = center_block[1] - block_h_offset
            y_end = center_block[1] + block_h_offset
            
            # Les blocs affiches n'ont pas change (on a pas assez bouge)
            if (x_start, x_end, y_start, y_end) == self.board_bounds[layer]:
                pass
            
            base.execute("SELECT block_id, block_x, block_y FROM blocks WHERE world=? AND layer_index=? AND block_x>=? AND block_x<=? AND block_y>=? AND block_y<=?", (self.world, layer, x_start, x_end, y_start, y_end))
            blocks = base.fetchall()
            
            for block in blocks:
                block_id, block_x, block_y = block
                
                # Le bloc est deja affiche, on ne le supprime pas
                if block_id in self.rendered_blocks.keys():
                    del blocks_to_remove[block_id]
                    print(block_id)
                    continue
                
                self.rendered_blocks[block_id] = (layer, block_x, block_y)
                self.helper.ws.insere(block_id, "div", parent="layer_" + str(layer))
                self.render_block(block_id, layer, block_x, block_y)
            
            self.board_bounds[layer] = (x_start, x_end, y_start, y_end)

        print(blocks_to_remove)
        for block_id in blocks_to_remove.keys():
            self.helper.ws.remove(block_id)
            del self.rendered_blocks[block_id]
            
        self.helper.ws.attributs("tiles", style={"left": str(-(self.origin[0]) + w / 2) + "px", "top": str(-(self.origin[1]) + h / 2) + "px"})

    def translate_direction(self, move: tuple):
        """
        Bouge la carte en utilisant les directions donnees par le vecteur move, on bouge en utilisant TRANSLATE_AMOUNT
        """
        if move == [0, 0]:
            return
        self.translate((move[0] * TRANSLATE_AMOUNT * self.zoom, move[1] * TRANSLATE_AMOUNT * self.zoom))

    
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

        # Utilises pour action, qui devrait sinon en initialiser beaucoup trop
        self.link = None
        self.base = None
        self.commit = False
        
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
        
    def create_layer(self, _, o: list[str, str, str, str]):
        self.layers[int(o[0])] = o[1]
        self.tile_pixel_sizes[int(o[0])] = int(o[2])
        self.block_pixel_sizes[int(o[0])] = int(o[2]) * BLOCKS_SIZE
        
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        base.execute("INSERT INTO layers VALUES (?,?,?,?,?);", (self.world, int(o[0]), o[1], int(o[2]), bool(o[3])))
        link.commit()
        
        self.helper.ws.insere("layer_" + o[0], "div", style={"z-index": int(o[0]) * 2}, parent="tiles")
        link.close()
        
    def delete_layer(self, _, o):
        if self.layer != int(o):
            raise ValueError("Il y a un probleme de synchronisation entre le client et le serveur, relancez.")
        
        self.helper.ws.remove("layer_option_" + str(self.layer))
        self.helper.ws.remove("layer_" + str(self.layer))
        del self.layers[self.layer]
        del self.tile_pixel_sizes[self.layer]
        del self.block_pixel_sizes[self.layer]
        
        link = sqlite3.connect(BOARD_PATH)
        base = link.cursor()
        
        base.execute("DELETE FROM layers WHERE world=? AND layer_index=?;", (self.world, self.layer))
        link.commit()
        
        link.close()
        
    def tool_changed(self, _m, o):
        self.tool = o

    def action(self, button: str, click_pos: tuple):
        def add_tile(block_pos, block_offsets, tile_pos):
            # On regarde s'il existe deja une tile
            # Sinon on la cree et on l'ajoute sur la page
            # Si oui, on la modifie dans la BD et sur la page
            # Tout en creant les blocks necessaires si besoin
            self.base.execute("SELECT block_id FROM blocks WHERE world=? AND layer_index=? AND block_x=? AND block_y=?;", (self.world, self.layer, block_pos[0], block_pos[1]))
            res = self.base.fetchall()
            block_id = ""
            if len(res) > 1:
                raise ValueError("Pas normal du tout")
            elif len(res) == 0:
                # On cree un nouveau block
                self.base.execute("INSERT INTO blocks(world,layer_index,block_x,block_y) VALUES (?,?,?,?);", (self.world, self.layer, block_pos[0], block_pos[1]))
                self.base.execute("SELECT block_id FROM blocks WHERE world=? AND layer_index=? AND block_x=? AND block_y=?;", (self.world, self.layer, block_pos[0], block_pos[1]))
                block_id = self.base.fetchone()[0]
                self.helper.ws.insere(block_id, "div", parent="layer_" + str(self.layer))
            else:
                block_id = res[0][0]
            
            self.base.execute("SELECT COUNT(image_name) FROM tiles WHERE block_id=? AND x=? AND y=?;", (block_id, tile_pos[0], tile_pos[1]))
            res = self.base.fetchall()[0][0]
            img_id = "_".join(map(str, [self.layer, block_pos[0] * self.block_size + tile_pos[0], block_pos[1] * self.block_size + tile_pos[1]]))
            if res > 1:
                raise ValueError("Pas normal du tout")
            elif res == 0:
                # On cree une nouvelle tile
                self.base.execute("INSERT INTO tiles VALUES (?,?,?,?);", (block_id, tile_pos[0], tile_pos[1], self.tile[:-4]))
                position = (self.zoom * (tile_pos[0] * self.tile_pixel_sizes[self.layer]) + block_offsets[0], self.zoom * (tile_pos[1] * self.tile_pixel_sizes[self.layer]) + block_offsets[1])
                path = TILESET_PATH.replace("%SET%", self.layers[self.layer]).replace("%IMG%", self.tile[:-4])
                self.helper.add_image_id(img_id, path, position, (self.zoom * self.tile_pixel_sizes[self.layer], self.zoom * self.tile_pixel_sizes[self.layer]), parent=block_id)
            else:
                # On modifie la tile d'avant
                self.base.execute("UPDATE tiles SET image_name = ? WHERE block_id=? AND x=? AND y=?;", (self.tile[:-4], block_id, tile_pos[0], tile_pos[1]))
                self.helper.ws.attributs(img_id, attr={'src': "../" + TILESET_PATH.replace("%SET%", self.layers[self.layer]).replace("%IMG%", self.tile[:-4])})
            
        def remove_tile(block_pos, tile_pos):        
            self.base.execute("SELECT block_id FROM blocks WHERE world=? AND layer_index=? AND block_x=? AND block_y=?;", (self.world, self.layer, block_pos[0], block_pos[1]))
            res = self.base.fetchall()
            block_id = ""
            if len(res) > 1:
                raise ValueError("Pas normal du tout")
            elif len(res) == 0:
                return
            
            block_id = res[0][0]
            
            self.base.execute("SELECT COUNT(image_name) FROM tiles WHERE block_id=? AND x=? AND y=?;", (block_id, tile_pos[0], tile_pos[1]))
            res = self.base.fetchall()[0][0]
            img_id = "_".join(map(str, [self.layer, block_pos[0] * self.block_size + tile_pos[0], block_pos[1] * self.block_size + tile_pos[1]]))
            if res > 1:
                raise ValueError("Pas normal du tout")
            elif res == 0:
                return
        
            # On modifie la tile d'avant
            self.base.execute("DELETE FROM tiles WHERE block_id=? AND x=? AND y=?;", (block_id, tile_pos[0], tile_pos[1]))
            self.helper.ws.remove(img_id)

        if self.link == None:
            self.link = sqlite3.connect(BOARD_PATH)
            self.commit = True
            try:
                self.link.autocommit = True
            except AttributeError:
                print("L'attribut autocommit n'est pas disponible pour sqlite3")
                self.commit = False
            self.base = self.link.cursor()
        
        x,y = click_pos[0] - self.origin[0], click_pos[1] - self.origin[1]
        
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
                # Il faudrait implementer une variable qui contienne la premiere position, quand on a la deuxieme on decide de quoi faire
                print("Ne fait rien pour l'instant")
            case _:
                raise TypeError("Il n'existe pas d'outil de ce type")
