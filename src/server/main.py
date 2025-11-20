from player import Player
from web.main_web import start
import web.inputs.keyboard
import web.inputs.mouse
import os

web_manager = None

def main():
    """
    Point d'entree du programme quand on lance le serveur
    """
    global web_manager
    
    try:
        lock = open("launched", "x")
        lock.close()
    except FileExistsError:
        print("Une instance du serveur est deja lancee")
        exit(0)
        return
    
    web_manager = start()
    
    # Gestionnaires inputs
    web_manager.gestionnaire_clavier(web.inputs.keyboard.handle_input)
    web_manager.gestionnaire_souris(web.inputs.mouse.handle_input)
        
    player = Player((50, 50))
    web.inputs.keyboard.add_event(player.move_input, "D", ["KeyW", "KeyA", "KeyS", "KeyD"])
    web.inputs.mouse.add_event(player.move_random, "U", [player.id])

def stop():
    """
    Fonction a appeler pour fermer **correctement** le serveur
    """
    web_manager.stop(fermer=False)
    
    os.remove("launched")
    
    exit(0)
    
# On verifie que le programme n'est pas importe mais bien lance
if __name__ == "__main__":
    main()
