from web.main_web import add_image, change_dimensions, get_window_size
import json
# on doit découper le fichier json de coordonnées des tiles pour launch le plateau
def load():
    with open("content/data/worlds/base_world.json", "r") as f:
        data = json.load(f)
        board = data["layers"][0]["tiles"]
        print(board)