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
header_col = (0, 0, 150) #colour for the header background

dis_width = 1280
dis_height = 920

header_height = 55
line_width = 3

play_height = dis_height-header_height

clock_speed = 60

dis=pg.display.set_mode((dis_width, dis_height))
pg.display.update()
pg.display.set_caption("Snake!")

clock = pg.time.Clock()

sprite_scale = 1.25
seg_length = 20 * sprite_scale
start_speed = 3
min_speed = 2
# How many food objects will spawn
num_food = 3
# How many types of food there are
num_food_types = 12
message_duration_max = 90
blindness_time_max = 300
blindness_time_phase = blindness_time_max / 10

tail_radius = 1/2 * seg_length
collision_radius = 3/4 * seg_length
safe_radius = 5 * seg_length

# rate at which speed changes when eating speed changing food
speed_inc = 1/2

save_file_name = "highscores.txt"

default_font = pg.font.get_default_font()
heading_font = "bahnschrift"
message_font = "comicsansms"
if heading_font not in pg.font.get_fonts():
    title_font = default_font

if message_font not in pg.font.get_fonts():
    message_font = default_font

font_style = pg.font.SysFont(heading_font, 40)
title_font = pg.font.SysFont(heading_font, 85)
high_score_font = pg.font.SysFont(heading_font, 45)
pause_font = pg.font.SysFont(heading_font, 85)
score_font = pg.font.SysFont(message_font, 30)
level_font = pg.font.SysFont(message_font, 35)
message_font = pg.font.SysFont(message_font, 35)

shadow_offset = 2

def load_image(name, scale = sprite_scale):
    fullname = os.path.join(sprites_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image.convert()
    return image, image.get_rect()

def display_text(msg, colour):
    msg_text = font_style.render(msg, True, colour)
    msg_rect = msg_text.get_rect(center=dis.get_rect().center)
    dis.blit(msg_text, msg_rect)

def pause_text(text):
    shadow = pause_font.render(text, True, black_col)
    to_print = pause_font.render(text, True, red_col)
    shadow_rect = shadow.get_rect(center=dis.get_rect().center)
    shadow_rect = shadow_rect.move(shadow_offset, shadow_offset)
    msg_rect = to_print.get_rect(center=dis.get_rect().center)
    dis.blit(shadow, shadow_rect)
    dis.blit(to_print, msg_rect)

def header_bar():
    header_rect = pg.Rect(0, 0, dis_width, header_height)
    pg.draw.rect(dis, header_col, header_rect)
    pg.draw.line(dis, black_col, (0, header_height-line_width), (dis_width, header_height-line_width), line_width)

def title_banner():
    msg_text = title_font.render("Snake!", True, green_col)
    msg_rect = msg_text.get_rect(midtop=(dis_width *1/2, dis_height*1/6))
    dis.blit(msg_text, msg_rect)

def print_scores():
    banner = high_score_font.render("High Scores:", True, green_col)
    f = open(save_file_name, "r")
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

def get_name(player):
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
        player.print_score()
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

def write_scores(player):
    if not os.path.isfile(save_file_name):
        with open(save_file_name, "w"):
            pass
    f = open(save_file_name, "r")
    score_list = f.readlines()
    f.close()
    score_dict = {}
    add_score = False
    if len(score_list) > 0:
        for entry in score_list:
            words = entry.split()
            score_dict[words[0]] = int(words[1])
            # if there are less than 10 scores, add the new one
        if len(score_dict) < 10:
            add_score = True
        else:
            # otherwise, add the new score if it is higher than a recorded one
            for record in score_dict:
                if player.score > score_dict[record]:
                    add_score = True
        score_dict = dict(sorted(score_dict.items(), key=lambda x:x[1], reverse=True))
    else:
        add_score = True
    if not add_score:
        return
    while len(score_dict) >= 10:
        score_dict.popitem()
    user_name = get_name(player)
    i = 0
    while user_name in score_dict:
        while user_name[-(i+1)].isnumeric():
            i += 1
        if i > 0:
            user_name = user_name[:-i] + str(int(user_name[-i:])+1)
        else:
            user_name += "1"
    score_dict[user_name] = player.score
    score_dict = dict(sorted(score_dict.items(), key=lambda x:x[1], reverse=True))
    f = open(save_file_name, "w")
    for record in score_dict:
        f.write(f"{record}    {score_dict[record]}\n")
    f.close()
    score_screen()

class Direction(IntEnum):
    UP = 0
    DOWN = 180
    LEFT = 90
    RIGHT = 270

class DestinationNode():
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        self.x = round(random.randrange(0, int(dis_width - seg_length)) / seg_length) * seg_length
        self.y = (round(random.randrange(0, int(play_height - seg_length)) / seg_length) * seg_length) + header_height

    def rotate(self,angle):
        self.image = pg.transform.rotate(self.image, angle)

class Snake(Sprite):
    def __init__(self):
        super().__init__()
        self.body = []
        self.length = 1
        self.speed = start_speed
        self.shields = 0
        self.glow = 0
        self.direction = Direction.UP
        self.seg_image_V = self.seg_image_H = self.shield_image = self.shield_rect = self.glow_image = None
        self.corner_UR = self.corner_RD = self.corner_DL = self.corner_LU = None
        self.blindness_time = 0
        self.blindness_levels = []
        self.blindness_rect = None
        self.load_sprites()
        self.body.append(self.Segment(self, self.x, self.y+seg_length, self.direction))
        self.body[0].destinations.append(DestinationNode(self.x, self.y))
        self.tail = self.body[0]
        
    def load_sprites(self):
        self.image, self.rect = load_image("Snake_Head.png")
        self.seg_image_V, self.rect = load_image("Snake_Body.png")
        self.seg_image_H = pg.transform.rotate(self.seg_image_V, Direction.RIGHT)
        self.shield_image, self.shield_rect = load_image("Spike_Shield.png")
        self.glow_image, self.glow_rect = load_image("Golden_Glow.png")
        self.corner2, self.rect = load_image("Snake_Corner2.png")
        self.cornerL1, self.rect = load_image("Snake_CornerL1.png")
        self.cornerR1, self.rect = load_image("Snake_CornerR1.png")
        self.tail_straight, self.rect = load_image("Snake_Tail.png")
        self.tail_turnL1, self.rect = load_image("Snake_Tail_TurnL1.png")
        self.tail_turnL2, self.rect = load_image("Snake_Tail_TurnL2.png")
        self.tail_turnR1, self.rect = load_image("Snake_Tail_TurnR1.png")
        self.tail_turnR2, self.rect = load_image("Snake_Tail_TurnR2.png")
        for i in range (1, 11):
            current_image, self.blindness_rect = load_image(f"Fog_of_Food-{i}.png")
            self.blindness_levels.append(current_image)

    def rotate(self,angle):
        self.image = pg.transform.rotate(self.image, angle)
        self.shield_image = pg.transform.rotate(self.shield_image, angle)
        self.glow_image = pg.transform.rotate(self.glow_image, angle)

    def place_object(self):
        self.x = dis_width / 2
        self.y = (play_height / 2) + header_height

    def display(self):
        dis.blit(self.image, (self.x, self.y))
        for segment in self.body:
            dis.blit(segment.image, (segment.x, segment.y))
        if self.shields > 0:
            self.shield_rect.center = pg.Rect(self.x, self.y, seg_length, seg_length).center
            dis.blit(self.shield_image, (self.shield_rect))
        if self.glow > 0:
            self.glow_rect.center = pg.Rect(self.x, self.y, seg_length, seg_length).center
            dis.blit(self.glow_image, (self.glow_rect))
        if self.blindness_time > 0:
            blind_image = self.process_blindness()
            self.blindness_rect.center = pg.Rect(self.x, self.y, seg_length, seg_length).center
            dis.blit(blind_image, (self.blindness_rect))
    
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
        self.body[-1].destinations.append(DestinationNode(self.tail.x, self.tail.y))
        self.tail.to_segment()
        self.tail.is_tail = False
        self.tail = self.body[-1]
        self.length += 1

    def change_direction(self, new_direction):
        angle = new_direction-self.direction
        self.direction = new_direction
        self.rotate(angle)

    def move(self):
        if self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed
        # check if the snake has collided with a screen edge
        if self.x >= dis_width or self.x < 0 or self.y >= dis_height or self.y < header_height:
            return False
        # create a new destination node
        next_destinations = [DestinationNode(self.x, self.y)]
        for i in range (self.length):
            # check if the snake has collided with its body
            if self.collide(self.body[i], tail_radius):
                return False
            # send the new destination node to the body
            next_destinations = self.body[i].move(next_destinations)
        return True

    def speed_up(self, multiplier = 1):
        self.speed += (speed_inc * multiplier)

    def slow_down(self):
        if self.speed - speed_inc <= min_speed:
            self.speed = min_speed
        else:
            self.speed -= speed_inc

    def activate_blindness(self):
        self.blindness_time = blindness_time_max

    def process_blindness(self):
        blindness_phase = math.ceil(self.blindness_time / blindness_time_phase)
        self.blindness_time -= 1
        return self.blindness_levels[blindness_phase-1]
    
    def get_mystery(self):
        number = round(random.randrange(0, 10))
        return number

    def mystery_effect(self, player):
        mystery_num = self.get_mystery()
        match mystery_num:
            case 0:
                player.update_message("One Bonus Point!")
                player.add_score(0, 1)
            case 1:
                player.update_message("Super Bonus Points!")
                player.add_score(3)
            case 2:
                player.update_message("ULTIMATE BONUS POINTS!!!")
                player.add_score(4)
            case 3:
                player.update_message("Spikes, yikes!")
                for j in range(3):
                    player.create_spikeball()
            case 4:
                player.update_message("Growww!")
                for j in range(3):
                    self.grow()
            case 5:
                player.update_message("Level Up?!?")
                player.level_up()
            case 6:
                player.update_message("Spikes And Shields, Madness!")
                for j in range(10):
                    player.create_spikeball()
                self.shields += 5
            case 7:
                player.update_message("Slow... down...")
                for j in range(3):
                    self.slow_down()
            case 8:
                player.update_message("Destroy Spikeballs!")
                for j in range(3):
                    if len(player.spikeballs) > 0:
                        del player.spikeballs[0]
            case 9:
                player.update_message("Fog of Food!")
                self.activate_blindness()
            case _:
                player.update_message("Nothing happened. Too bad.")
                        
    class Segment(Sprite):
        def __init__(self, head, x, y, direction):
            self.x = x
            self.y = y
            self.head = head
            self.is_tail = True
            self.direction = direction
            self.from_direction = None
            self.previous_direction = self.direction
            self.from_distance = 0
            self.next_direction = direction
            self.destinations = []
            self.image, self.rect = head.tail_straight, head.rect
            self.rotate(direction-Direction.UP)

        def move(self, new_destinations):
            # add new destinations to the destination list
            self.destinations.extend(new_destinations)
            self.update_next_direction()
            # create a list to hold newly reached destinations to pass to the next segment
            passed_destinations = []
            # keep track of the current segment's total movement for this frame
            movement = self.head.speed
            # while there is more movement to be done, and there are still destinations to reach
            while movement > 0:
                distance = self.calc_distance(self, self.destinations[0])
                move_range = self.calc_movement_range(distance, movement)
                if self.direction == Direction.UP:
                    self.y -= move_range
                elif self.direction == Direction.DOWN:
                    self.y += move_range
                elif self.direction == Direction.LEFT:
                    self.x -= move_range
                else:
                    self.x += move_range
                movement -= move_range
                self.from_distance += move_range
                # this segment has reached the current destination
                if distance == 0:
                    current_dir = self.direction
                    passed_destinations.append(self.destinations.pop(0))
                    self.update_direction(self.calc_direction(self, self.destinations[0]))
                    self.update_next_direction()
                    if self.direction != current_dir:
                        self.previous_direction = current_dir
                        self.from_distance = 0

            self.update_sprite()
            return passed_destinations
        
        def calc_distance(self, position1, position2):
            return max(abs(position1.y - position2.y), abs(position1.x - position2.x))
            
        def calc_next_turn(self):
            distance = self.calc_distance(self, self.destinations[0])
            i = 1
            turn_direction = self.direction
            while turn_direction == self.direction and i < len(self.destinations):
                distance += self.calc_distance(self.destinations[i-1], self.destinations[i])
                turn_direction = self.calc_direction(self.destinations[i-1], self.destinations[i])
                i += 1
            if turn_direction == self.direction:
                return float('inf'), turn_direction
            return distance, turn_direction
            
        def calc_direction(self, position1, position2):
            if position1.x > position2.x:
                return Direction.LEFT
            elif position1.x < position2.x:
                return Direction.RIGHT
            elif position1.y > position2.y:
                return Direction.UP
            else:
                return Direction.DOWN
        
        def calc_movement_range(self, distance, movement):
            if distance <= movement:
                return distance
            if distance > movement:
                return movement
        
        def rotate(self,angle):
            self.image = pg.transform.rotate(self.image, angle)

        def update_direction(self, new_direction):
            self.from_direction = self.direction
            self.direction = new_direction

        def update_next_direction(self):
            if len(self.destinations) > 1:
                self.next_direction = self.calc_direction(self.destinations[0], self.destinations[1])
        
        def update_sprite(self):
            # Check the distance to the next turn, and the absolute direction of the turn
            turn_distance, abs_turn_direction = self.calc_next_turn()
            # If the next turn is close, turn the segment
            if turn_distance < (2*seg_length)/3:
                if self.is_tail:
                    self.turn_tail(turn_distance, abs_turn_direction)
                else:
                    self.turn_segment(turn_distance, abs_turn_direction)
            # Otherwise the segment will be going straight
            else: 
                if self.is_tail:
                    self.to_tail()
                else:
                    # If the segment is still in the process of turning, it should be curved
                    if self.from_distance > 0 and self.from_distance < (2*seg_length)/3:
                        self.finish_turn()
                    # Otherwise, it will be a straight segment
                    else:
                        self.to_segment()

        def turn_tail(self, turn_distance, abs_turn_direction):
            # Determine if this is a left turn or right turn
            tail_turn_dir = self.direction - abs_turn_direction
            if abs(tail_turn_dir) > 90:
                tail_turn_dir *= -1
            # Check if this is the first or second stage of a turn
            if turn_distance < seg_length/3:
                if tail_turn_dir > 0:
                    self.image = self.head.tail_turnR2
                else:
                    self.image = self.head.tail_turnL2
            else:
                if tail_turn_dir > 0:
                    self.image = self.head.tail_turnR1
                else:
                    self.image = self.head.tail_turnL1
            self.rotate(self.direction)

        def finish_turn(self):
            # Determine if this is a left turn or right turn
            seg_turn_dir = self.previous_direction - self.direction
            if abs(seg_turn_dir) > 90:
                seg_turn_dir *= -1
            # Check if this is the first or second stage of a turn
            if self.from_distance < seg_length/3:
                self.image = self.head.corner2
                if self.direction is Direction.LEFT and self.previous_direction is Direction.DOWN \
                    or self.direction is Direction.UP and self.previous_direction is Direction.RIGHT:
                    self.rotate(Direction.RIGHT)
                elif self.direction is Direction.RIGHT and self.previous_direction is Direction.DOWN \
                    or self.direction is Direction.UP and self.previous_direction is Direction.LEFT:
                    self.rotate(Direction.DOWN)
                elif self.direction is Direction.RIGHT and self.previous_direction is Direction.UP \
                    or self.direction is Direction.DOWN and self.previous_direction is Direction.LEFT:
                    self.rotate(Direction.LEFT)
            else:
                if seg_turn_dir < 0:
                    self.image = self.head.cornerR1
                    self.rotate(Direction.RIGHT)
                else:
                    self.image = self.head.cornerL1
                    self.rotate(Direction.LEFT)
                self.rotate(self.previous_direction)

        def turn_segment(self,turn_distance, abs_turn_direction):
            # Determine if this is a left turn or right turn
            seg_turn_dir = self.direction - abs_turn_direction
            if abs(seg_turn_dir) > 90:
                seg_turn_dir *= -1
            # Check if this is the first or second stage of a turn
            if turn_distance < seg_length/3:
                self.image = self.head.corner2
                if abs_turn_direction is Direction.LEFT and self.direction is Direction.DOWN \
                    or abs_turn_direction is Direction.UP and self.direction is Direction.RIGHT:
                    self.rotate(Direction.RIGHT)
                elif abs_turn_direction is Direction.RIGHT and self.direction is Direction.DOWN \
                    or abs_turn_direction is Direction.UP and self.direction is Direction.LEFT:
                    self.rotate(Direction.DOWN)
                elif abs_turn_direction is Direction.RIGHT and self.direction is Direction.UP \
                    or abs_turn_direction is Direction.DOWN and self.direction is Direction.LEFT:
                    self.rotate(Direction.LEFT)
            else:
                if seg_turn_dir > 0:
                    self.image = self.head.cornerR1
                else:
                    self.image = self.head.cornerL1
                self.rotate(self.direction)

        def to_segment(self):
            if self.direction == Direction.LEFT or self.direction == Direction.RIGHT:
                self.image = self.head.seg_image_H
            else:
                self.image = self.head.seg_image_V

        def to_tail(self):
            self.image = self.head.tail_straight
            self.rotate(self.direction)          

class Spikeball(Sprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image("Spike_Ball.png")
        self.rect.center = self.x, self.y

class FoodNum(IntEnum):
    # number keys for each type of food
    GLOW = 1
    SLOW = 2
    BONUS = 3
    MYSTERY = 4
    SHIELD = 5
    NORMAL = 0

foodType = {
    FoodNum.GLOW: {
        "rarity": 10,
        "sprite": "Glow_Food.png"
    },
    FoodNum.SLOW: {
        "rarity": 10,
        "sprite": "Slow_Food.png"
    },
    FoodNum.BONUS: {
        "rarity": 15,
        "sprite": "Bonus_Food.png"
    },
    FoodNum.MYSTERY: {
        "rarity": 8,
        "sprite": "Mystery_Food.png"
    },
    FoodNum.SHIELD: {
        "rarity": 5,
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


class Food(Sprite):
    def __init__(self):
        super().__init__()
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

class Player():
    def __init__(self, snake):
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.curr_message = ""
        self.message_duration = 0
        self.spikeballs = []
        self.foods = []
        self.snake = snake
        for i in range(num_food):
            self.foods.append(None)
            self.create_food(i)

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
        speed_increment = (self.level // 5) + 1
        self.snake.speed_up(speed_increment)
    
    def create_spikeball(self):
        valid_space = False
        while not valid_space:
            self.spikeballs.append(Spikeball())
            valid_space = True
            # if the new spikeball is close to the snake's head, it is not valid
            if self.spikeballs[-1].collide(self.snake, safe_radius):
                valid_space = False
            if valid_space:
                # if the new spikeball is within the snake's body, it is not valid
                for segment in self.snake.body:
                    if self.spikeballs[-1].collide(segment, collision_radius):
                        valid_space = False
            if valid_space:
                # if the new spikeball is in the same space as a piece of food, it is not valid
                for food in self.foods:
                    if self.spikeballs[-1].collide(food, collision_radius):
                        valid_space = False
            if valid_space:
                # if the new spikeball is in the same space as another spikeball, it is not valid
                for ball in self.spikeballs[:-1]:
                    if self.spikeballs[-1].collide(ball, collision_radius):
                        valid_space = False
            # if the new spikeball is in an invalid location, delete it and create another
            if not valid_space:
                del self.spikeballs[-1]
        
    def create_food(self, index):
        valid_space = False
        while not valid_space:
            self.foods[index] = (Food())
            valid_space = True
            # if the new food is close to the snake's head, it is not valid
            if self.foods[index].collide(self.snake, safe_radius):
                valid_space = False
            if valid_space:
                # if the new food is within the snake's body, it is not valid
                for segment in self.snake.body:
                    if self.foods[index].collide(segment, collision_radius):
                        valid_space = False
            if valid_space:
                # if the new spikeball is in the same space as a piece of food, it is not valid
                for food in self.foods[:index]:
                    if self.foods[index].collide(food, collision_radius):
                        valid_space = False
                for food in self.foods[index+1:]:
                    if self.foods[index].collide(food, collision_radius):
                        valid_space = False
            if valid_space:
                # if the new food is in the same space as a spikeball, it is not valid
                for ball in self.spikeballs[:-1]:
                    if self.foods[index].collide(ball, collision_radius):
                        valid_space = False
            # if the new spikeball is in an invalid location, the loop will replace it

    def update_message(self, text):
        self.curr_message = text
        self.message_duration = message_duration_max

    def print_score(self):
        value = score_font.render("Score: " + str(self.score), True, black_col)
        dis.blit(value, [0 + shadow_offset, 0 + shadow_offset])
        value = score_font.render("Score: " + str(self.score), True, yellow_col)
        dis.blit(value, [0, 0])

    def print_level(self):
        value = level_font.render("Level: " + str(self.level), True, black_col)
        dis.blit(value, [dis_width*7/8 + shadow_offset, 0 + shadow_offset])
        value = level_font.render("Level: " + str(self.level), True, yellow_col)
        dis.blit(value, [dis_width*7/8, 0])

    def print_shields(self):
        value = level_font.render("Shields: " + str(self.snake.shields), True, black_col)
        dis.blit(value, [dis_width*2/5 + shadow_offset, 0 + shadow_offset])
        value = level_font.render("Shields: " + str(self.snake.shields), True, yellow_col)
        dis.blit(value, [dis_width*2/5, 0])

    def print_food_text(self):
        shadow = message_font.render(self.curr_message, True, black_col)
        to_print = message_font.render(self.curr_message, True, yellow_col)
        shadow_rect = shadow.get_rect(midtop=(dis_width *1/2, header_height*2))
        shadow_rect = shadow_rect.move(shadow_offset, shadow_offset)
        msg_rect = to_print.get_rect(midtop=(dis_width *1/2, header_height*2))
        dis.blit(shadow, shadow_rect)
        dis.blit(to_print, msg_rect)

def start_screen():
    play = False
    while not play:
        dis.fill(black_col)
        title_banner()
        display_text("Press P-Play, S-See High Scores, Q-Quit Game", white_col)
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
    game_paused = False

    snake = Snake()
    player = Player(snake)

    start_screen()

    while not game_close:
        while game_over == True:
            dis.fill(black_col)
            display_text("Game Over! Press any key to continue", red_col)
            player.print_score()
            pg.display.update()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_over = False
                    game_close = True
                if event.type == pg.KEYDOWN:
                    write_scores(player)
                    gameLoop()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_close = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    snake.change_direction(Direction.LEFT)
                elif event.key == pg.K_RIGHT:
                    snake.change_direction(Direction.RIGHT)
                elif event.key == pg.K_UP:
                    snake.change_direction(Direction.UP)
                elif event.key == pg.K_DOWN:
                    snake.change_direction(Direction.DOWN)
                elif event.key == pg.K_SPACE:
                    game_paused = not game_paused

        if game_paused:
            pause_text("- Game Paused -")
            pg.display.update()
        else:    
            dis.fill(background_col)
            header_bar()
            for food in player.foods:
                food.display()
            if snake.move() is False:
                game_over = True
            player.print_score()
            player.print_level()
            player.print_shields()
                
            for ball in player.spikeballs:
                ball.display()
            snake.display()
            if player.message_duration > 0:
                player.print_food_text()
                player.message_duration -= 1
            pg.display.update()
            for spikeball in player.spikeballs:
                if spikeball.collide(snake, collision_radius):
                    if snake.shields > 0:
                        snake.shields -= 1
                        player.spikeballs.remove(spikeball)
                    else:
                        game_over = True
            for i in range(len(player.foods)):
                if player.foods[i].collide(snake, collision_radius):
                    snake.grow()
                    player.add_score()
                    if snake.glow > 0:
                        snake.glow -= 1
                    match player.foods[i].type:
                        case FoodNum.GLOW:
                            snake.glow += 1
                            player.update_message("Golden Glow! Double the next food's score!")
                        case FoodNum.SLOW:
                            snake.slow_down()
                            player.update_message("Speed Decreased")
                        case FoodNum.BONUS:
                            player.add_score(2)
                            player.update_message("Bonus Points!")
                        case FoodNum.SHIELD:
                            if snake.shields == 0:
                                player.update_message("Spike Shield Activated!")
                            else:
                                player.update_message("Spike Shield Increased!")
                            snake.shields += 1
                        case FoodNum.MYSTERY:
                            snake.mystery_effect(player)
                        case _:
                            pass
                    player.create_food(i)
                    player.eat_food()
                    break
        clock.tick(clock_speed)

    pg.quit()
    quit()

def main():
    gameLoop()

main()
