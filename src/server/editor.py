import os # remove, listdir, path.isfile
import time # time
import threading # Threading
import sqlite3

import wsinter
import web_helper

import graphics.board
from inputs.keyboard import Keyboard
from inputs.mouse import Mouse

editor = None

TILESET_PATH = "assets/tilesets/%SET%/%IMG%.png"

def main():
    global editor
    
    try:
        lock = open("launched", "x")
        lock.close()
    except FileExistsError:
        print("Une instance du serveur est deja lancee")
        exit(0)
        return
    
    editor = Editor(start_page = "editor.html")
    
def stop():
    global editor
    editor.stop()
    
    os.remove("launched")
    exit(0)
    
class Editor:
    def __init__(self, start_page: str):
        self.web_manager = wsinter.Inter("content/pages/" + start_page)
        self.web_manager.demarre(clavier=True)
        
        self.web_helper = web_helper.Helper(self.web_manager)
        
        self.link = sqlite3.connect("content/data/worlds/worlds.db")
        self.base = self.link.cursor()
        
        # Dictionnaire du numero de couche vers la tileset qui lui correspond
        self.layers: dict[int, str] = {}
        self.add_elements()
        
        self.layer: int = 0
        self.tile: str = ""
        
        self.keyboard_manager = Keyboard(self.web_manager)
        self.mouse_manager = Mouse(self.web_manager)
        
        self.loop_thread = threading.Thread(target=self.loop)
        self.loop_thread.start()
    
    def add_elements(self):
        # On ajoute tous les mondes possibles
        self.base.execute("SELECT name FROM worlds;")
        worlds = self.base.fetchall()
        if len(worlds) == 1:
            self.world_changed(None, worlds[0][0])
        for world in worlds:
            self.web_manager.insere(world[0], "option", attr={"value":world[0]}, parent="world")
            self.web_manager.inner_text(world[0], world[0])
            
        # On ajoute toutes les tilesets possibles
        for file in os.listdir("content/assets/tilesets"):
            if os.path.isfile("content/assets/tilesets" + file):
                continue
            self.web_manager.insere(file, "option", attr={"value":file}, parent="tileset-choice")
            self.web_manager.inner_text(file, file)                
        
        # On crée des gestionnaires pour les divers evenements
        self.web_manager.gestionnaire("world_changed", self.world_changed)
        self.web_manager.gestionnaire("layer_changed", self.layer_changed)
        self.web_manager.gestionnaire("create_layer", self.create_layer)
        self.web_manager.gestionnaire("delete_layer", self.delete_layer)
        self.web_manager.gestionnaire("tile_changed", self.tile_changed)
    
    def world_changed(self, _, o: str):
        self.world = o
        
        # On charge le plateau
        self.board = graphics.board.Board(self.web_helper, self.world, 16, 16)
        
        # Ajoute les elements pour ce monde precis
        self.base.execute("SELECT layer_index,tileset,collisions FROM layers WHERE world=? ORDER BY layer_index ASC;", (self.world,))
        layers = self.base.fetchall()
        layers = [list(layer) for layer in layers]
        self.web_manager.injecte("addLayers(" + str(layers) + ")")
        
        for layer in layers:
            # On map les couches avec leur tileset
            self.layers[layer[0]] = layer[1]
            self.board.load(layer[0])
        
    def layer_changed(self, _, o: int):
        self.layer = int(o)
        
        # On supprime tout d'abord
        self.web_manager.remove_children("tileset")
        
        tileset_path = "/assets/tilesets/" + self.layers[self.layer] + "/"
        # Charge les images
        i = 0
        for file in os.listdir("content" + tileset_path):
            self.web_manager.insere("palette_" + str(i), "img", attr={'src':'../' + tileset_path + file}, parent="tileset")
            i += 1
            
        self.web_manager.injecte("addTilesEvent();")
        
    def tile_changed(self, _, o):
        self.tile = o
        
    def create_layer(self, _, o: list[str, str, str]):
        self.layers[int(o[0])] = o[1]
        self.board.create_layer([int(o[0]), o[1], bool(o[2])])
        
    def delete_layer(self, _, o):
        if self.layer != int(o):
            raise ValueError("Il y a un probleme de synchronisation entre le client et le serveur, relancez.")
        
        self.web_manager.remove("layer_option_" + str(self.layer))
        self.web_manager.remove("layer_" + str(self.layer))
        del self.layers[self.layer]
        self.board.remove_layer(self.layer)
            
    def loop(self):
        self.do_loop = True
        last_loop_time = 0
        
        while self.do_loop:
            delta_time = time.time() - last_loop_time
            if delta_time < 0.017:
                continue
            
            keys = self.keyboard_manager.get_keys()
            buttons = self.mouse_manager.get_buttons()
            
            # Si le bouton gauche est appuye
            if buttons[0]["L"] and self.tile != "":
                # On map ces positions vers un bloc, puis vers une tile dans ce bloc
                # Pour ce faire, on considere pour l'instant que le 0,0 est en haut à gauche
                x,y = buttons[1]
                # On calcule la taille en pixels d'un bloc
                block_pixel_size = 16 * 16
                # On effectue la division euclidienne des coos par le nombre de pixels d'un bloc
                block_x, block_y = x // block_pixel_size, y // block_pixel_size
                # Puis on effectue la division euclidienne du reste des coos par le nombre de pixels d'un bloc, par le nombre de pixels d'une tile
                tile_x, tile_y = (x - block_x * block_pixel_size) // 16, (y - block_y * block_pixel_size) // 16
            
                img_id = "_".join(map(str, [self.layer, block_x * 16 + tile_x, block_y * 16 + tile_y]))
                self.web_manager.attributs(img_id, attr={'src': "../" + TILESET_PATH.replace("%SET%", self.layers[self.layer]).replace("%IMG%", self.tile[:-4])})
            
            last_loop_time = time.time()
            
    def stop(self):
        self.do_loop = False
        self.loop_thread.join()
        self.web_manager.stop()
        
if __name__ == "__main__":
    main()