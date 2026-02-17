import os # remove
import time # time
import threading # Threading
from math import sqrt

import wsinter
import web_helper

import graphics.board
from characters.player import Player
from characters.enemy import Enemy
from characters.npc import Interactable, Npc
from inputs.keyboard import Keyboard
from inputs.mouse import Mouse

from cProfile import Profile
from pstats import SortKey, Stats

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

    game = Game("index.html")

def stop():
    global game
    game.stop()

    os.remove("launched")
    exit(0)

class Game:
    def __init__(self, start_page: str = "index.html"):
        """
        Point d'entree du programme quand on lance le serveur
        """
        self.web_manager = wsinter.Inter("content/pages/" + start_page)
        self.web_manager.demarre(clavier=True)

        self.web_helper = web_helper.Helper(self.web_manager)

        # Gestionnaires inputs
        self.keyboard_manager = Keyboard(self.web_manager)
        self.mouse_manager = Mouse(self.web_manager)

        # Pour l'instant, le joueur doit rester en premier, car il a du style sur #img0
        self.player = Player(self.web_helper, (50, 50))
        self.web_manager.attributs(self.player.id, style={"z-index": 10})

        self.board = graphics.board.Board(self.web_helper, "spawn")

        # TODO: Gérer les NPC avec les tiles, et les ajouter au fil qu'on se rapproche pour pas avoir tous les NPC ici du monde H24
        # On crée une lste de NPC pour pouvoir en gérer plusieurs plus facilement
        self.npc: list[Npc] = []
        base_npc_1 = Npc(self.web_helper, (200, 100), "assets/spritesheets/blue_haired_woman/blue_haired_woman_001.png", dialogs="dialog1")
        base_npc_2 = Npc(self.web_helper, (150, 250), "assets/spritesheets/blue_haired_woman/blue_haired_woman_009.png", dialogs="dialog2")
        self.npc.append(base_npc_1)
        self.npc.append(base_npc_2)

        # TODO: De la meme maniere que les NPC, les ajouter avec la map
        self.enemies: list[Enemy] = []
        base_enemy = Enemy(self.web_helper, (600, 300), "assets/spritesheets/blonde_man/blonde_man_010.png", 50)
        self.enemies.append(base_enemy)

        # TODO: Passer dans player ?
        self.interactable: Interactable = None

        self.keyboard_manager.subscribe_event(self.interact_key_handler, "D", ['KeyE', 'ArrowUp', 'ArrowLeft', 'ArrowDown', 'ArrowRight', 'Enter'])

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
            case 'ArrowUp' | 'ArrowLeft' | 'ArrowDown' | 'ArrowRight' | 'Enter':
                if self.interactable.is_opened():
                    self.interactable.key(key)

    def loop(self):
        """
        Contient la boucle principale

        On vise 60 images par secondes, donc 60 iterations par seconde, faire plus serait consommer beaucoup de ressources pour pas grand chose

        Pour la physique on pourrait meme viser 30 iterations par seconde

        Ainsi on conditionne le temps
        """
        with Profile() as profile:
            self.do_loop = True
            last_loop_time = time.time()

            while self.do_loop:
                delta_time = time.time() - last_loop_time
                # 1 / 60 ~= 0.017, on s'embete pas à faire le calcul tout le temps, on pourrait limite stocker la duree dans une variable mais pas tres utile non plus
                if delta_time < 0.017:
                    continue

                last_loop_time = time.time()


                keys = self.keyboard_manager.get_keys()

                # On actualise la liste des ennemis en supprimant ceux qui sont morts
                for enemy in self.enemies:
                    if enemy.is_dead():
                        self.enemies.remove(enemy)

                # Toutes les instructions ici sont mises en pauses lorsqu'un menu est ouvert par le joueur
                if self.interactable is None or not self.interactable.is_opened():
                    in_range_enemies = []
                    player_range = self.player.weapon.range
                    for enemy in self.enemies:
                        enemy.update(delta_time, self.player)
                        dst = sqrt((enemy.x - self.player.x) ** 2 + (enemy.y - self.player.y) ** 2)
                        if dst <= player_range:
                            in_range_enemies.append(enemy)
                    if not self.player.is_dead():
                        player_movement = self.player.update(delta_time, keys, in_range_enemies)
                        self.board.translate(player_movement)

                self.interactable = None
                for npc in self.npc:
                    if npc.within_distance(self.player.get_position()):
                        self.interactable = npc
                        self.web_manager.inner_text("action-bar", "Appuyez sur E pour interagir")

                if self.interactable == None:
                    self.web_manager.inner_text("action-bar", "")

            (
                Stats(profile)
                .strip_dirs()
                .sort_stats(SortKey.CUMULATIVE)
                .print_stats()
            )

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
