from constants import (
    NUM_FOOD,
    SAFE_RADIUS,
    COLLISION_RADIUS,
    MESSAGE_DURATION_MAX,
    SHADOW_OFFSET,
    DIS_WIDTH,
    HEADER_HEIGHT,
    BLACK_COL,
    YELLOW_COL
)
from interactables import Food, Spikeball

class Player():
    def __init__(self, snake, dis, fonts):
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.curr_message = ""
        self.message_duration = 0
        self.spikeballs = []
        self.foods = []
        self.snake = snake
        self.dis = dis
        self.fonts = fonts
        for i in range(NUM_FOOD):
            self.foods.append(None)
            self.create_food(i)
        self.dis = dis
        self.fonts = fonts

    def add_score(self, multiplier = 1, adder = 0):
        if self.snake.glow > 0:
            multiplier *= 2
        self.score += (self.level * multiplier) + adder

    def eat_food(self, quantity = 1):
        self.food_eaten += quantity
        while self.food_eaten >= 10:
            self.food_eaten -= 10
            self.level_up()
    
    def level_up(self):
        self.level += 1
        for i in range((self.level // 5) +1):
            self.create_spikeball()
        speed_increment = (self.level // 10) + 1
        self.snake.speed_up(speed_increment)
    
    def create_spikeball(self):
        valid_space = False
        while not valid_space:
            self.spikeballs.append(Spikeball(self.dis))
            valid_space = True
            # if the new spikeball is close to the snake's head, it is not valid
            if self.spikeballs[-1].collide(self.snake, SAFE_RADIUS):
                valid_space = False
            if valid_space:
                # if the new spikeball is within the snake's body, it is not valid
                for segment in self.snake.body:
                    if self.spikeballs[-1].collide(segment, COLLISION_RADIUS):
                        valid_space = False
            if valid_space:
                # if the new spikeball is in the same space as a piece of food, it is not valid
                for food in self.foods:
                    if self.spikeballs[-1].collide(food, COLLISION_RADIUS):
                        valid_space = False
            if valid_space:
                # if the new spikeball is in the same space as another spikeball, it is not valid
                for ball in self.spikeballs[:-1]:
                    if self.spikeballs[-1].collide(ball, COLLISION_RADIUS):
                        valid_space = False
            # if the new spikeball is in an invalid location, delete it and create another
            if not valid_space:
                del self.spikeballs[-1]
        
    def create_food(self, index):
        valid_space = False
        while not valid_space:
            self.foods[index] = (Food(self.dis))
            valid_space = True
            # if the new food is close to the snake's head, it is not valid
            if self.foods[index].collide(self.snake, SAFE_RADIUS):
                valid_space = False
            if valid_space:
                # if the new food is within the snake's body, it is not valid
                for segment in self.snake.body:
                    if self.foods[index].collide(segment, COLLISION_RADIUS):
                        valid_space = False
            if valid_space:
                # if the new spikeball is in the same space as a piece of food, it is not valid
                for food in self.foods[:index]:
                    if self.foods[index].collide(food, COLLISION_RADIUS):
                        valid_space = False
                for food in self.foods[index+1:]:
                    if self.foods[index].collide(food, COLLISION_RADIUS):
                        valid_space = False
            if valid_space:
                # if the new food is in the same space as a spikeball, it is not valid
                for ball in self.spikeballs[:-1]:
                    if self.foods[index].collide(ball, COLLISION_RADIUS):
                        valid_space = False
            # if the new spikeball is in an invalid location, the loop will replace it

    def update_message(self, text):
        self.curr_message = text
        self.message_duration = MESSAGE_DURATION_MAX

    def print_score(self):
        value = self.fonts["header_font"].render("Score: " + str(self.score), True, BLACK_COL)
        self.dis.blit(value, [0 + SHADOW_OFFSET, 0 + SHADOW_OFFSET])
        value = self.fonts["header_font"].render("Score: " + str(self.score), True, YELLOW_COL)
        self.dis.blit(value, [0, 0])

    def print_level(self):
        value = self.fonts["header_font"].render("Level: " + str(self.level), True, BLACK_COL)
        self.dis.blit(value, [DIS_WIDTH*7/8 + SHADOW_OFFSET, 0 + SHADOW_OFFSET])
        value = self.fonts["header_font"].render("Level: " + str(self.level), True, YELLOW_COL)
        self.dis.blit(value, [DIS_WIDTH*7/8, 0])

    def print_shields(self):
        value = self.fonts["header_font"].render("Shields: " + str(self.snake.shields), True, BLACK_COL)
        self.dis.blit(value, [DIS_WIDTH*2/5 + SHADOW_OFFSET, 0 + SHADOW_OFFSET])
        value = self.fonts["header_font"].render("Shields: " + str(self.snake.shields), True, YELLOW_COL)
        self.dis.blit(value, [DIS_WIDTH*2/5, 0])

    def print_food_text(self):
        shadow = self.fonts["message_font"].render(self.curr_message, True, BLACK_COL)
        to_print = self.fonts["message_font"].render(self.curr_message, True, YELLOW_COL)
        shadow_rect = shadow.get_rect(midtop=(DIS_WIDTH *1/2, HEADER_HEIGHT*2))
        shadow_rect = shadow_rect.move(SHADOW_OFFSET, SHADOW_OFFSET)
        msg_rect = to_print.get_rect(midtop=(DIS_WIDTH *1/2, HEADER_HEIGHT*2))
        self.dis.blit(shadow, shadow_rect)
        self.dis.blit(to_print, msg_rect)
