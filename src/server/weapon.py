import time

class Weapon:
    def __init__(self, damage: int, range: int, cooldown: float, durability: int=-1):
        self.damage = damage
        self.range = range
        self.cooldown = cooldown
        self.durability = durability

        self.last_attack = time.time()
        