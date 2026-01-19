import os # remove
import time # time
import threading # Threading
import sqlite3

import wsinter
import web_helper

import graphics.board
from inputs.keyboard import Keyboard
import inputs.mouse

editor = None

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
        
        #self.board = graphics.board.Board(self.web_helper, "test_world")
        #self.board.load(0)
        
        self.link = sqlite3.connect("content/data/worlds/worlds.db")
        self.base = self.link.cursor()
        
        self.add_elements()
        
        self.keyboard_manager = Keyboard(self.web_manager)
        self.web_manager.gestionnaire_souris(inputs.mouse.handle_input)
        
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
        
        # On crée un gestionnaire pour le changement de monde
        self.web_manager.gestionnaire("world_changed", self.world_changed)
        self.web_manager.gestionnaire("layer_changed", self.layer_changed)
    
    def world_changed(self, _, o: str):
        self.world = o
        print(o)
        
        # Ajoute les elements pour ce monde precis
        self.base.execute("SELECT layer_index,tileset,collisions FROM layers WHERE world=? ORDER BY layer_index ASC;", (self.world,))
        layers = self.base.fetchall()
        layers = [list(layer) for layer in layers]
        self.web_manager.injecte("addLayers(" + str(layers) + ")")
        
    def layer_changed(self, _, o: int):
        self.layer = o
        print(self.layer)
    
    def loop(self):
        self.do_loop = True
        last_loop_time = 0
        
        while self.do_loop:
            delta_time = time.time() - last_loop_time
            if delta_time < 0.017:
                continue
            
            keys = self.keyboard_manager.get_keys()
            
            last_loop_time = time.time()
            
    def stop(self):
        self.do_loop = False
        self.loop_thread.join()
        self.web_manager.stop()
        
if __name__ == "__main__":
    main()