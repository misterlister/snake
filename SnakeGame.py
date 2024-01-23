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

snake_seg = 20
start_speed = 8
# How many food objects will spawn
num_food = 3
# How many types of food there are
num_food_types = 10
message_duration_max = 50
min_speed = 4

# rate at which speed changes when eating speed changing food
speed_inc = 2

def load_image(name, scale = 1):
    fullname = os.path.join(sprites_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image.convert()
    return image, image.get_rect()

class Food(IntEnum):
    # key for speed increasing food
    SPEED = 1
    # key for speed decreasing food
    SLOW = 2
    # key for food that gives bonus points
    BONUS = 3
    # key for mystery food
    MYSTERY = 4
    # key for shield food
    SHIELD = 5

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
    value = score_font.render("Your Score: " + str(score), True, black_col)
    dis.blit(value, [0 + shadow_offset, 0 + shadow_offset])
    value = score_font.render("Your Score: " + str(score), True, yellow_col)
    dis.blit(value, [0, 0])

def your_level(level):
    value = level_font.render("Level: " + str(level), True, black_col)
    dis.blit(value, [dis_width*2/3 + shadow_offset, 0 + shadow_offset])
    value = level_font.render("Level: " + str(level), True, yellow_col)
    dis.blit(value, [dis_width*2/3, 0])

def food_message(message):
    shadow = message_font.render(message, True, black_col)
    to_print = message_font.render(message, True, yellow_col)
    shadow_rect = shadow.get_rect(center=dis.get_rect().center)
    shadow_rect = shadow_rect.move(shadow_offset, shadow_offset)
    msg_rect = to_print.get_rect(center=dis.get_rect().center)
    dis.blit(shadow, shadow_rect)
    dis.blit(to_print, msg_rect)

def our_snake(snake_list):
    for x in snake_list:
        pg.draw.rect(dis, black_col, [x[0], x[1], snake_seg, snake_seg])

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

def place_object(axis):
    coordinate = round(random.randrange(0, axis - snake_seg) / snake_seg) * snake_seg
    return coordinate

def set_food_type():
    food_type = round(random.randrange(0, num_food_types))
    return food_type

def draw_object(x_coord, y_coord, o_type):
    if o_type == Food.SPEED:
        pg.draw.rect(dis, speed_col, [x_coord, y_coord, snake_seg, snake_seg])
    elif o_type == Food.SLOW:
        pg.draw.rect(dis, slow_col, [x_coord, y_coord, snake_seg, snake_seg])
    elif o_type == Food.BONUS:
        pg.draw.rect(dis, bonus_col, [x_coord, y_coord, snake_seg, snake_seg])
    else:
        pg.draw.rect(dis, green_col, [x_coord, y_coord, snake_seg, snake_seg])

class Spikeball(pg.sprite.Sprite):

    def __init__(self):
        #pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("spikeball.png")
        self.x = place_object(dis_width)
        self.y = place_object(dis_height)
        self.rect.center = self.x, self.y

    def display(self):
        dis.blit(self.image, (self.x, self.y))

def collide(x1, y1, x2, y2):
    if (x1 - x2 <= snake_seg/4*3 and x1 - x2 >= -snake_seg/4*3) and (y1 - y2 <= snake_seg/4*3 and y1 - y2 >= -snake_seg/4*3):
        return True
    return False


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

    x1 = dis_width / 2
    y1 = dis_height / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    length_of_snake = 1
    snake_speed = start_speed

    game_score = 0
    game_level = 1
    previous_level = 1
    curr_message = ""
    message_duration = 0

    # handles creation of spikeballs. 
    spikeball_ready = False

    spikeballs = []

    foodx = [0] * num_food
    for x in range(num_food):
        foodx[x] = place_object(dis_width)

    foody = [0] * num_food
    for y in range(num_food):
        foody[y] = place_object(dis_height)

    foodt = [0] * num_food
    for t in range(num_food):
        foodt[t] = set_food_type()

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
                    x1_change = -snake_speed
                    y1_change = 0
                elif event.key == pg.K_RIGHT:
                    x1_change = snake_speed
                    y1_change = 0
                elif event.key == pg.K_UP:
                    x1_change = 0
                    y1_change = -snake_speed
                elif event.key == pg.K_DOWN:
                    x1_change = 0
                    y1_change = snake_speed

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_over = True

        # The next spike ball will be created when length is a multiple of 10
        if length_of_snake % 10 == 9:
            spikeball_ready = True

        if length_of_snake % 10 == 0 and spikeball_ready:
            spikeball_ready = False
            spikeballs.append(Spikeball())
        
        x1 += x1_change
        y1 += y1_change
        dis.fill(background_col)
        for j in range(num_food):
            draw_object(foodx[j], foody[j], foodt[j])
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x ==snake_head:
                game_over = True

        our_snake(snake_list)
        your_score(game_score)
        your_level(game_level)
        if message_duration > 0:
            food_message(curr_message)
            message_duration -= 1
            
        for ball in spikeballs:
            ball.display()
        pg.display.update()
        for spikeball in spikeballs:
            if collide(x1, y1, spikeball.x, spikeball.y):
                game_over = True
        for i in range(num_food):
            if collide(x1, y1, foodx[i], foody[i]):
                if foodt[i] == Food.SPEED:
                    snake_speed += speed_inc
                    curr_message = "Speed Up!!!"
                    message_duration = message_duration_max
                elif foodt[i] == Food.SLOW:
                    if snake_speed - speed_inc <= min_speed:
                        snake_speed = min_speed
                    else:
                        snake_speed -= speed_inc
                    curr_message = "Slow down..."
                    message_duration = message_duration_max
                elif foodt[i] == Food.BONUS:
                    game_score += game_level * 2
                    curr_message = "Bonus Points!"
                    message_duration = message_duration_max
                foodx[i] = place_object(dis_width)
                foody[i] = place_object(dis_height)
                foodt[i] = set_food_type()
                length_of_snake += 1
                game_score += game_level
                game_level = math.ceil(length_of_snake/10)
                if game_level > previous_level:
                    snake_speed += speed_inc
                    previous_level = game_level
                break
        clock.tick(clock_speed)

    pg.quit()
    quit()

def main():
    gameLoop()

main()