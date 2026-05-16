from characters.npc import Interactable
import web_helper

IMAGE_PATH = "assets/spritesheets/blue_haired_woman/blue_haired_woman_008.png"

class Waypoint(Interactable):
    def __init__(self, helper: web_helper.Helper, position: tuple, destination: tuple, distance: int = 30):
        self.helper = helper
        self.position = position
        self.distance = distance
        self.destination = destination
        self.width = self.height = 64
        


        self.opened = False

        self.id = self.helper.add_image(IMAGE_PATH, self.position, size=(self.width, self.height), parent='tiles')

    def interact(self):
        self.opened = True
        
    def is_opened(self):
        return self.opened
    
    def key(self):
        pass
