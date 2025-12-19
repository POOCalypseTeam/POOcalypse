import os # remove
import time # time, sleep
import threading # Threading

# Réorganiser player et npc pour respecter la structure et pas avoir des fichiers n'importe où dans la racine
from player import Player
from npc import Interactable, Npc
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

        time.sleep(0.5)
        
        # Pour l'instant, le joueur doit rester en premier, car il a du style sur #img0
        self.player = Player((50, 50))
        
        # TODO: Gérer les NPC avec les tiles, et les ajouter au fil qu'on se rapproche pour pas avoir tous les NPC ici du monde H24
        # On crée une lste de NPC pour pouvoir en gérer plusieurs plus facilement
        self.npc: list[Npc] = []
        base_npc_1 = Npc(self.web_manager, (200, 100), "assets/spritesheets/blue_haired_woman/blue_haired_woman_001.png", dialogs="dialog1")
        base_npc_2 = Npc(self.web_manager, (150, 250), "assets/spritesheets/blue_haired_woman/blue_haired_woman_009.png", dialogs="dialog2")
        self.npc.append(base_npc_1)
        self.npc.append(base_npc_2)
        
        self.interactable: Interactable = None
        
        self.keyboard_manager.subscribe_event(self.interact_key_handler, "D", ['KeyE', 'ArrowLeft', 'ArrowRight', 'Enter'])
        
        # On lance la boucle principale
        self.loop_thread = threading.Thread(target=self.loop)
        self.loop_thread.start()
        
    def interact_key_handler(self, key):
        if self.interactable == None or not issubclass(type(self.interactable), Interactable):
            return
        match key:
            case 'KeyE':
                if not self.interactable.is_opened():
                    self.interactable.interact()
            case 'ArrowLeft' | 'ArrowRight' | 'Enter':
                if self.interactable.is_opened():
                    self.interactable.key(key)

    def loop(self):
        """
        Contient la boucle principale
        
        On vise 60 images par secondes, donc 60 iterations par seconde, faire plus serait consommer beaucoup de ressources pour pas grand chose
        
        Poour la physique on pourrait meme viser 30 iterations par seconde
        
        Ainsi on conditionne le temps
        """
        self.do_loop = True
        last_loop_time = 0
        
        while self.do_loop:
            delta_time = time.time() - last_loop_time
            # 1 / 60 ~= 0.017, on s'embete pas à faire le calcul tout le temps, on pourrait limite stocker la duree dans une variable mais pas tres utile non plus
            if delta_time < 0.017:
                continue
            
            keys = self.keyboard_manager.get_keys()
            
            self.player.update(delta_time, keys)
            
            self.interactable = None
            for npc in self.npc:
                if npc.within_distance(self.player.get_position()):
                    self.interactable = npc
                    self.web_manager.inner_text("action-bar", "Appuyez sur E pour interagir")
                    
            if self.interactable == None:
                self.web_manager.inner_text("action-bar", "")
                
            last_loop_time = time.time()

    def stop(self):
        """
        Fonction a appeler pour fermer **correctement** le serveur
        """
        self.do_loop = False
        self.loop_thread.join()
        self.web_manager.stop()
    
# On verifie que le programme n'est pas importe mais bien lance
if __name__ == "__main__":
    main()
