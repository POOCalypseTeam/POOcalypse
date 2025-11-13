import web.main_web
import web.inputs.keyboard
import web.inputs.mouse

web_manager = None

def main():
    """
    Point d'entree du programme quand on lance le serveur
    """
    global web_manager
    # TODO: Etablir un verrou pour pas lancer deux fois le serveur
    # TODO: Reattribuer le port a cette instance si pas bien ferme avant
    web_manager = web.main_web.start()
    
    # Gestionnaires inputs
    web_manager.gestionnaire_clavier(web.inputs.keyboard.handle_input)
    web_manager.gestionnaire_souris(web.inputs.mouse.handle_input)
    

def stop():
    """
    Fonction a appeler pour fermer **correctement** le serveur
    """
    web_manager.stop(fermer=False)
    exit(0)
    
# On verifie que le programme n'est pas importe mais bien lance
if __name__ == "__main__":
    main()
