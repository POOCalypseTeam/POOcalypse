import json

import web_helper

class Board:
    def __init__(self, helper: web_helper.Helper, layer):
        with open("content/data/worlds/base_world.json", "r") as f:
            self.data = json.load(f)
        self.helper = helper
        self.layer = layer

    def load(self):
        board = self.data["layers"][self.layer]["tiles"]
        IMG_PATH = "assets/tilesets/basic/grass/"
        IMG_SIZE = 32
        # on créer une liste de dictionnaires à partir du json
        for t in board:
            img_id = self.helper.add_image(IMG_PATH+t["tile"]+".png",(t["x"]*IMG_SIZE,t["y"]*IMG_SIZE),(IMG_SIZE,IMG_SIZE), None, "div_board"+str(self.layer))
