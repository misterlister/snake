# 
# This "Snake" game is based off of the Edureka tutorial found at https://www.edureka.co/blog/snake-game-with-pygame/
# All additional features and implementation were designed and implemented by Hayden Lister
#

import pygame as pg
import time
import random
import math
import os
import os.path
from enum import IntEnum

pg.init()

main_dir = os.path.split(os.path.abspath(__file__))[0]
sprites_dir = os.path.join(main_dir, "sprites")

black_col = (0, 0, 0) #colour for snake
background_col = (205, 225, 255) #colour for the main background screen
green_col = (0, 155, 0) #colour for normal food
red_col = (255, 0, 0) #colour for game over text
white_col = (255, 255, 255) #colour for the background of the game over screen
yellow_col = (255, 215, 0) #colour for score and food effect text

bonus_col = (0, 255, 0) #colour for bonus points food
speed_col = (255, 0, 255) #colour for speed food
slow_col = (120, 0, 120) #colour for slow food

dis_width = 1280
dis_height = 720

clock_speed = 30

dis=pg.display.set_mode((dis_width, dis_height))
pg.display.update()
pg.display.set_caption("Snake!")

clock = pg.time.Clock()

seg_length = 20
start_speed = 6
# How many food objects will spawn
num_food = 3
# How many types of food there are
num_food_types = 12
message_duration_max = 50
min_speed = 4

tail_radius = 1/2 * seg_length
collision_radius = 3/4 * seg_length
safe_radius = 5 * seg_length

# rate at which speed changes when eating speed changing food
speed_inc = 1

def load_image(name, scale = 1):
    fullname = os.path.join(sprites_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image.convert()
    return image, image.get_rect()

class FoodNum(IntEnum):
    
    # key for speed increasing food
    SPEED = 1
    SPEEDRARITY = 10
    # key for speed decreasing food
    SLOW = 2
    SLOWRARITY = 10
    # key for food that gives bonus points
    BONUS = 3
    BONUSRARITY = 15
    # key for mystery food
    MYSTERY = 4
    MYSTERYRARITY = 8
    # key for shield food
    SHIELD = 5
    SHIELDRARITY = 5

    SPECIALRARITY = SPEEDRARITY + SLOWRARITY + BONUSRARITY + MYSTERYRARITY + SHIELDRARITY

    NORMAL = 0
    NORMALRARITY = SPECIALRARITY

    TOTALRARITY = NORMALRARITY + SPECIALRARITY

class Direction(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

save_name = "highscores.txt"

default_font = pg.font.get_default_font()
heading_font = "bahnschrift"
message_font = "comicsansms"
if heading_font not in pg.font.get_fonts():
    title_font = default_font

if message_font not in pg.font.get_fonts():
    message_font = default_font

font_style = pg.font.SysFont(heading_font, 25)
title_font = pg.font.SysFont(heading_font, 65)
high_score_font = pg.font.SysFont(heading_font, 45)
score_font = pg.font.SysFont(message_font, 30)
level_font = pg.font.SysFont(message_font, 35)
message_font = pg.font.SysFont(message_font, 35)

shadow_offset = 2

def your_score(score):
    value = score_font.render("Score: " + str(score), True, black_col)
    dis.blit(value, [0 + shadow_offset, 0 + shadow_offset])
    value = score_font.render("Score: " + str(score), True, yellow_col)
    dis.blit(value, [0, 0])

def your_level(level):
    value = level_font.render("Level: " + str(level), True, black_col)
    dis.blit(value, [dis_width*7/8 + shadow_offset, 0 + shadow_offset])
    value = level_font.render("Level: " + str(level), True, yellow_col)
    dis.blit(value, [dis_width*7/8, 0])

def your_shields(shields):
    value = level_font.render("Shields: " + str(shields), True, black_col)
    dis.blit(value, [dis_width*2/5 + shadow_offset, 0 + shadow_offset])
    value = level_font.render("Shields: " + str(shields), True, yellow_col)
    dis.blit(value, [dis_width*2/5, 0])

def food_message(message):
    shadow = message_font.render(message, True, black_col)
    to_print = message_font.render(message, True, yellow_col)
    shadow_rect = shadow.get_rect(center=dis.get_rect().center)
    shadow_rect = shadow_rect.move(shadow_offset, shadow_offset)
    msg_rect = to_print.get_rect(center=dis.get_rect().center)
    dis.blit(shadow, shadow_rect)
    dis.blit(to_print, msg_rect)

def message(msg, colour):
    msg_text = font_style.render(msg, True, colour)
    msg_rect = msg_text.get_rect(center=dis.get_rect().center)
    dis.blit(msg_text, msg_rect)

def title_banner():
    msg_text = title_font.render("Snake!", True, green_col)
    msg_rect = msg_text.get_rect(midtop=(dis_width *1/2, dis_height*1/6))
    dis.blit(msg_text, msg_rect)

def print_scores():
    banner = high_score_font.render("High Scores:", True, green_col)
    f = open(save_name, "r")
    score_list = f.readlines()
    banner_rect = banner.get_rect(midtop=(dis_width *1/2, dis_height*1/15))
    score_renders = []
    score_rects = []
    dis.blit(banner, banner_rect)
    while (len(score_list) > 10):
        score_list.pop()
    for i in range (0, len(score_list)):
        score_list[i] = score_list[i][:-1]
        score_renders.append(score_font.render(f"Rank {i+1}:    {score_list[i]}", True, yellow_col))
        score_rects.append(score_renders[i].get_rect(midtop=(dis_width *1/2, (dis_height*i/(15))+ dis_height/5)))
        dis.blit(score_renders[i], score_rects[i])
    f.close()

def get_name(score):
    title_text = high_score_font.render("You got a High Score! Enter your name:", True, green_col)
    title_rect = title_text.get_rect(midtop=(dis_width *1/2, dis_height*1/6))
    user_text = ""
    input_rect = pg.Rect(dis_width/3, dis_height/2, dis_width/4, dis_height/15)
    done = False
    while not done:
        dis.fill(black_col)
        pg.draw.rect(dis, yellow_col, input_rect)
        text_surface = font_style.render(user_text, True, black_col)
        dis.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        input_rect.w = max(100, text_surface.get_width()+10)
        dis.blit(title_text, title_rect)
        your_score(score)
        pg.display.update()
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                    done = True
                else:
                    user_text += event.unicode
    if user_text == "":
        user_text = "Unnamed"
    return user_text

def write_scores(score):
    if not os.path.isfile(save_name):
        with open(save_name, "w"):
            pass
    f = open(save_name, "r")
    score_list = f.readlines()
    f.close()
    score_dict = {}
    add_score = False
    if len(score_list) > 0:
        for entry in score_list:
            words = entry.split()
            score_dict[words[0]] = int(words[1])
        if len(score_dict) < 10:
            add_score = True
        else:
            for record in score_dict:
                if score > score_dict[record]:
                    add_score = True
        score_dict = dict(sorted(score_dict.items(), key=lambda x:x[1], reverse=True))
    else:
        add_score = True
    if not add_score:
        return
    while len(score_dict) >= 10:
        score_dict.popitem()
    user_name = get_name(score)
    i = 0
    while user_name in score_dict:
        while user_name[-(i+1)].isnumeric():
            i += 1
        if i > 0:
            user_name = user_name[:-i] + str(int(user_name[-i:])+1)
        else:
            user_name += "1"
    score_dict[user_name] = score
    score_dict = dict(sorted(score_dict.items(), key=lambda x:x[1], reverse=True))
    f = open(save_name, "w")
    for record in score_dict:
        f.write(f"{record}    {score_dict[record]}\n")
    f.close()
    score_screen()


class Sprite():
    def __init__(self):
        self.image, self.rect = None, None
        self.x, self.y = None, None
        self.place_object()
        
    def display(self):
        dis.blit(self.image, (self.x, self.y))

    def collide(self, obj, radius):
        if (obj.x - self.x <= radius and obj.x - self.x >= -radius):
            if (obj.y - self.y <= radius and obj.y - self.y >= -radius):
                return True
        return False
    
    def place_object(self):
        self.x = round(random.randrange(0, dis_width - seg_length) / seg_length) * seg_length
        self.y = round(random.randrange(0, dis_height - seg_length) / seg_length) * seg_length

class Snake(Sprite):
    def __init__(self):
        super().__init__()
        self.body = []
        self.length = 1
        self.speed = start_speed
        self.shields = 0
        self.direction = Direction.UP
        self.body.append(self.Segment(self, self.x, self.y+seg_length, self.direction))#
        self.body[0].destinations.append((self.x, self.y))
        self.tail = self.body[0]
        self.image, self.rect = load_image("Spike_Ball.png")#HEAD
        
    def place_object(self):
        self.x = dis_width / 2
        self.y = dis_height / 2
    def display(self):
        #pg.draw.rect(dis, black_col, [self.x, self.y, seg_length, seg_length])
        dis.blit(self.image, (self.x, self.y))#
        for segment in self.body:
            dis.blit(segment.image, (segment.x, segment.y))#
            #pg.draw.rect(dis, black_col, [segment.x, segment.y, seg_length, seg_length])
    
    def grow(self):
        if self.tail.direction == Direction.UP:
            new_x = self.tail.x
            new_y = self.tail.y + seg_length
        elif self.tail.direction == Direction.DOWN:
            new_x = self.tail.x
            new_y = self.tail.y - seg_length
        elif self.tail.direction == Direction.LEFT:
            new_x = self.tail.x + seg_length
            new_y = self.tail.y
        else:
            new_x = self.tail.x - seg_length
            new_y = self.tail.y
        self.body.append(self.Segment(self, new_x, new_y, self.tail.direction))
        self.body[-1].destinations.append((self.tail.x, self.tail.y))
        self.tail.image, self.tail.rect = load_image("Spike_Ball.png")#SEGMENT
        self.tail = self.body[-1]
        self.length += 1

    def move(self):
        if self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed
        if self.x >= dis_width or self.x < 0 or self.y >= dis_height or self.y < 0:
            return False
        next_destinations = [(self.x, self.y)]
        for i in range (self.length):
            if self.collide(self.body[i], tail_radius):
                return False
            next_destinations = self.body[i].move(next_destinations)
        return True

    def speed_up(self):
        self.speed += speed_inc

    def slow_down(self):
        self.speed -= speed_inc

    class Segment():
        def __init__(self, head, x, y, direction):
            self.x = x
            self.y = y
            self.head = head
            self.direction = direction
            self.destinations = []
            self.image, self.rect = load_image("Slow_Food.png")#TAIL

        def move(self, new_destinations):
            self.destinations.extend(new_destinations)
            passed_destinations = []
            movement = self.head.speed
            while movement > 0 and len(self.destinations) > 0:
                if self.x != self.destinations[0][0]:
                    if self.x > self.destinations[0][0]:
                        self.x -= 1
                        self.direction = Direction.LEFT
                    else:
                        self.x += 1
                        self.direction = Direction.RIGHT
                    movement -= 1
                elif self.y != self.destinations[0][1]:
                    if self.y > self.destinations[0][1]:
                        self.y -= 1
                        self.direction = Direction.UP
                    else:
                        self.y += 1
                        self.direction = Direction.DOWN
                    movement -= 1
                else:
                    passed_destinations.append(self.destinations.pop(0)) 
            return passed_destinations

class Spikeball(Sprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image("Spike_Ball.png")
        self.rect.center = self.x, self.y

class Food(Sprite):
    def __init__(self):
        super().__init__()
        self.type = None
        self.sprite = None
        self.__get_type_and_sprite()
        self.image, self.rect = load_image(self.sprite)
        self.rect.center = self.x, self.y

    def __get_type_and_sprite(self):
        type_code = round(random.randrange(0, FoodNum.TOTALRARITY))
        if type_code - FoodNum.SPEEDRARITY <= 0:
            self.sprite = "Speed_Food.png"
            self.type = FoodNum.SPEED
            return
        if type_code - FoodNum.SLOWRARITY <= 0:
            self.sprite = "Slow_Food.png"
            self.type = FoodNum.SLOW
            return
        if type_code - FoodNum.BONUSRARITY <= 0:
            self.sprite = "Bonus_Food.png"
            self.type = FoodNum.BONUS
            return
        if type_code - FoodNum.MYSTERYRARITY <= 0:
            self.sprite = "Mystery_Food.png"
            self.type = FoodNum.MYSTERY
            return
        if type_code - FoodNum.SHIELDRARITY <= 0:
            self.sprite = "Shield_Food.png"
            self.type = FoodNum.SHIELD
            return
        else:
            self.sprite = "Normal_Food.png"
            self.type = FoodNum.NORMAL

def start_screen():
    play = False
    while not play:
        dis.fill(black_col)
        title_banner()
        message("Press P-Play, S-See High Scores, Q-Quit Game", white_col)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    score_screen()
                if event.key == pg.K_p:
                    play = True
                if event.key == pg.K_q:
                    pg.quit()
                    quit()


def score_screen():
    done = False
    while not done:
        dis.fill(black_col)
        print_scores()
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                done = True

def gameLoop():
    game_over = False
    game_close = False

    snake = Snake()

    game_score = 0
    game_level = 1
    previous_level = 1
    curr_message = ""
    message_duration = 0

    spikeballs = []
    foods = []

    for i in range(num_food):
        foods.append(Food())

    start_screen()

    while not game_close:
        while game_over == True:
            dis.fill(black_col)
            message("Game Over! Press any key to continue", red_col)
            your_score(game_score)
            pg.display.update()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_over = False
                    game_close = True
                if event.type == pg.KEYDOWN:
                    write_scores(game_score)
                    gameLoop()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_close = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    snake.direction = Direction.LEFT
                elif event.key == pg.K_RIGHT:
                    snake.direction = Direction.RIGHT
                elif event.key == pg.K_UP:
                    snake.direction = Direction.UP
                elif event.key == pg.K_DOWN:
                    snake.direction = Direction.DOWN

        dis.fill(background_col)
        for food in foods:
            food.display()
        if snake.move() is False:
            game_over = True
        snake.display()
        your_score(game_score)
        your_level(game_level)
        your_shields(snake.shields)
        if message_duration > 0:
            food_message(curr_message)
            message_duration -= 1
            
        for ball in spikeballs:
            ball.display()
        pg.display.update()
        for spikeball in spikeballs:
            if spikeball.collide(snake, collision_radius):
                if snake.shields > 0:
                    snake.shields -= 1
                    spikeballs.remove(spikeball)
                else:
                    game_over = True
        for i in range(len(foods)):
            if foods[i].collide(snake, collision_radius):
                if foods[i].type == FoodNum.SPEED:
                    snake.speed_up()
                    curr_message = "Speed Up!!!"
                elif foods[i].type == FoodNum.SLOW:
                    if snake_speed - speed_inc <= min_speed:
                        snake_speed = min_speed
                    else:
                        snake.slow_down()
                    curr_message = "Slow down..."
                elif foods[i].type == FoodNum.BONUS:
                    game_score += game_level * 2
                    curr_message = "Bonus Points!"
                elif foods[i].type == FoodNum.MYSTERY:
                    game_score += game_level * 2
                    curr_message = "MYSTERY!"
                elif foods[i].type == FoodNum.SHIELD:
                    snake.shields += 1
                    curr_message = "Spike Shield Active!"
                if foods[i].type != FoodNum.NORMAL:
                    message_duration = message_duration_max
                foods[i] = Food()
                snake.grow()
                game_score += game_level
                game_level = math.ceil(snake.length/10)
                if game_level > previous_level:
                    snake.speed_up()
                    previous_level = game_level
                    for i in range((game_level // 5) +1):
                        spikeballs.append(Spikeball())
                    
                break
        clock.tick(clock_speed)

    pg.quit()
    quit()

def main():
    gameLoop()

main()