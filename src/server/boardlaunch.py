from web.main_web import add_image, change_dimensions, get_window_size
import json

map = [["000","251","000"],
       ["251","000","251"],
       ["000","251","000"]]
# on doit découper le fichier json de coordonnées des tiles pour launch le plateau
def load():
    with open("content/data/worlds/base_world.json", "r") as f:
        data = json.load(f)
        board = data["layers"][0]["tiles"]
        IMG_PATH = "assets/tilesets/basic/grass/"
        IMG_SIZE = 32
        # on créer une liste de dictionnaires à partir du json
        for t in board:
            idimg = add_image(IMG_PATH+t["tile"]+".png",(t["x"]*IMG_SIZE,t["y"]*IMG_SIZE),(IMG_SIZE,IMG_SIZE))
            

def load_map():
    IMG_PATH = "assets/tilesets/basic/grass/grass_"
    IMG_SIZE = 32
    for y in range(len(map)):
        for x in range(len(map[0])):
            id = add_image(IMG_PATH+map[x][y]+".png",(x*IMG_SIZE,y*IMG_SIZE),(IMG_SIZE,IMG_SIZE))

def add_tile(x,y,tile):
    """
    Modifie la case de coordonnées x,y
    
    tile : string
    x,y : integer
    """
    try:
        map[x][y] = tile
    except:
        raise ValueError("BRUUUUUUH cheeeeeeeef ? Les bonnes valeurs peut-être non ?")

class Board:
    def __init__(self,layer):
        with open("content/data/worlds/base_world.json", "r") as f:
            self.data = json.load(f)
        self.layer = layer
    def load(self):
        board = self.data["layers"][self.layer]["tiles"]
        IMG_PATH = "assets/tilesets/basic/grass/"
        IMG_SIZE = 32
        # on créer une liste de dictionnaires à partir du json
        for t in board:
            idimg = add_image(IMG_PATH+t["tile"]+".png",(t["x"]*IMG_SIZE,t["y"]*IMG_SIZE),(IMG_SIZE,IMG_SIZE),self.layer*2)
