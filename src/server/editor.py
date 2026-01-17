import os # remove
import time # time
import threading # Threading

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
        
        self.keyboard_manager = Keyboard(self.web_manager)
        self.web_manager.gestionnaire_souris(inputs.mouse.handle_input)
        
        self.loop_thread = threading.Thread(target=self.loop)
        self.loop_thread.start()
        
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