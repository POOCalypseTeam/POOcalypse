import os # remove
import time # time, sleep
import threading # Threading

from player import Player
import web.main_web # start
from web.inputs.keyboard import Keyboard
import web.inputs.mouse

game = None

def main():
    global game
    
    try:
        lock = open("launched", "x")
        lock.close()
    except FileExistsError:
        print("Une instance du serveur est deja lancee")
        exit(0)
        return
    
    game = Game()
    
def stop():
    global game
    game.stop()
    
    os.remove("launched")
    exit(0)

class Game:
    def __init__(self):
        """
        Point d'entree du programme quand on lance le serveur
        """        
        self.web_manager = web.main_web.start()
        
        # Gestionnaires inputs
        self.keyboard_manager = Keyboard(self.web_manager)
        self.web_manager.gestionnaire_souris(web.inputs.mouse.handle_input)
            
        self.player = Player((50, 50))
        
        # On lance la boucle principale
        self.loop_thread = threading.Thread(target=self.loop)
        self.loop_thread.start()

    def loop(self):
        """
        Contient la boucle principale
        
        On vise 60 images par secondes, donc 60 iterations par seconde, faire plus serait consommer beaucoup de ressources pour pas grand chose
        
        Poour la physique on pourrait meme viser 30 iterations par seconde
        
        Ainsi on conditionne le temps
        """
        self.do_loop = True
        last_loop_time = time.time()
        
        while self.do_loop:
            delta_time = time.time() - last_loop_time
            # 1 / 60 ~= 0.017, on s'embete pas à faire le calcul tout le temps, on pourrait limite stocker dans une variable mais pas tres utile non plus
            if delta_time < 0.017:
                continue
            
            keys = self.keyboard_manager.get_keys()
            self.player.update(delta_time, keys)
            
            last_loop_time = time.time()

    def stop(self):
        """
        Fonction a appeler pour fermer **correctement** le serveur
        """
        self.do_loop = False
        self.loop_thread.join()
        self.web_manager.stop(fermer=False)
    
# On verifie que le programme n'est pas importe mais bien lance
if __name__ == "__main__":
    main()
