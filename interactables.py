from constants import (
    FoodNum
)
from sprite import Sprite, load_image
import random

class Food(Sprite):
    def __init__(self, dis):
        super().__init__(dis)
        self.type = None
        self.sprite = None
        self.__get_type_and_sprite()
        self.image, self.rect = load_image(self.sprite)
        self.rect.center = self.x, self.y

    def __get_type_and_sprite(self):
        type_code = round(random.randrange(0, total_rarity))
        for type in FoodNum:
            type_code -= foodType[type]["rarity"]
            if type_code <= 0:
                self.sprite = foodType[type]["sprite"]
                self.type = type
                return

foodType = {
    FoodNum.GLOW: {
        "rarity": 15,
        "sprite": "Glow_Food.png"
    },
    FoodNum.SLOW: {
        "rarity": 5,
        "sprite": "Slow_Food.png"
    },
    FoodNum.BONUS: {
        "rarity": 20,
        "sprite": "Bonus_Food.png"
    },
    FoodNum.MYSTERY: {
        "rarity": 8,
        "sprite": "Mystery_Food.png"
    },
    FoodNum.SHIELD: {
        "rarity": 6,
        "sprite": "Shield_Food.png"
    },
    FoodNum.NORMAL: {
        "rarity": 50,
        "sprite": "Normal_Food.png"
    }
}

# generates the total of all rarity variables, to use for random generation
total_rarity = 0
for food in foodType:
    total_rarity += foodType[food]["rarity"]

class Spikeball(Sprite):
    def __init__(self, dis):
        super().__init__(dis)
        self.image, self.rect = load_image("Spike_Ball.png")
        self.rect.center = self.x, self.y

