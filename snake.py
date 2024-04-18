import pygame as pg
from sprite import Sprite, load_image
import random
from constants import (
    START_SPEED,
    Direction,
    SEG_LENGTH,
    DIS_WIDTH,
    DIS_HEIGHT,
    PLAY_HEIGHT,
    BLINDNESS_TIME_MAX,
    TRANSPARENT,
    HEADER_HEIGHT,
    TAIL_RADIUS,
    SPEED_INC,
    MIN_SPEED
)

class Snake(Sprite):
    def __init__(self, dis):
        super().__init__(dis)
        self.body = []
        self.length = 1
        self.speed = START_SPEED
        self.shields = 0
        self.glow = 0
        self.direction = Direction.UP
        self.seg_image_V = self.seg_image_H = self.shield_image = self.shield_rect = self.glow_image = None
        self.corner_UR = self.corner_RD = self.corner_DL = self.corner_LU = None
        self.blindness_time = 0
        self.load_sprites()
        self.body.append(Segment(self, self.x, self.y+SEG_LENGTH, self.direction))
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

    def rotate(self,angle):
        self.image = pg.transform.rotate(self.image, angle)
        self.shield_image = pg.transform.rotate(self.shield_image, angle)
        self.glow_image = pg.transform.rotate(self.glow_image, angle)

    def place_object(self):
        self.x = DIS_WIDTH / 2
        self.y = (PLAY_HEIGHT / 2) + HEADER_HEIGHT

    def display(self):
        self.rect.center = (self.x, self.y)
        self.dis.blit(self.image, (self.rect))
        for segment in self.body:
            segment.rect.center = (segment.x, segment.y)
            self.dis.blit(segment.image, (segment.rect))
        if self.shields > 0:
            self.shield_rect.center = (self.x, self.y)
            self.dis.blit(self.shield_image, (self.shield_rect))
        if self.glow > 0:
            self.glow_rect.center = (self.x, self.y)
            self.dis.blit(self.glow_image, (self.glow_rect))
        if self.blindness_time > 0:
            blind_surface = pg.Surface((DIS_WIDTH,PLAY_HEIGHT))
            blind_surface.set_colorkey(TRANSPARENT)
            if self.blindness_time > BLINDNESS_TIME_MAX * (2/3) :
                blindness_radius = BLINDNESS_TIME_MAX + 100 - (self.blindness_time)
            elif self.blindness_time > BLINDNESS_TIME_MAX /3:
                blindness_radius = BLINDNESS_TIME_MAX * (5/3) + 100 - (self.blindness_time * 2)
            else:
                blindness_radius = BLINDNESS_TIME_MAX * (6/3) + 100 - (self.blindness_time * 3)
            self.blindness_time -= 1
            pg.draw.circle(blind_surface, TRANSPARENT, (self.x, self.y - HEADER_HEIGHT), blindness_radius)
            self.dis.blit(blind_surface, (0, HEADER_HEIGHT))
    
    def grow(self):
        if self.tail.direction == Direction.UP:
            new_x = self.tail.x
            new_y = self.tail.y + SEG_LENGTH
        elif self.tail.direction == Direction.DOWN:
            new_x = self.tail.x
            new_y = self.tail.y - SEG_LENGTH
        elif self.tail.direction == Direction.LEFT:
            new_x = self.tail.x + SEG_LENGTH
            new_y = self.tail.y
        else:
            new_x = self.tail.x - SEG_LENGTH
            new_y = self.tail.y
        self.body.append(Segment(self, new_x, new_y, self.tail.direction))
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
        if self.x >= DIS_WIDTH or self.x < 0 or self.y >= DIS_HEIGHT or self.y < HEADER_HEIGHT:
            return False
        # create a new destination node
        next_destinations = [DestinationNode(self.x, self.y)]
        for i in range (self.length):
            # check if the snake has collided with its body
            if self.collide(self.body[i], TAIL_RADIUS):
                return False
            # send the new destination node to the body
            next_destinations = self.body[i].move(next_destinations)
        return True

    def speed_up(self, multiplier = 1):
        self.speed += (SPEED_INC * multiplier)

    def slow_down(self):
        if self.speed - SPEED_INC <= MIN_SPEED:
            self.speed = MIN_SPEED
        else:
            self.speed -= SPEED_INC

    def activate_blindness(self):
        self.blindness_time = BLINDNESS_TIME_MAX
    
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
                for j in range(self.length // 5):
                    self.grow()
            case 5:
                player.update_message("Free Level Up!")
                player.level_up()
            case 6:
                player.update_message("Spikes And Shields, Madness!")
                for j in range(10):
                    player.create_spikeball()
                self.shields += 5
            case 7:
                player.update_message("Slow... down...")
                for j in range(2):
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
        if turn_distance < (2*SEG_LENGTH)/3:
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
                if self.from_distance > 0 and self.from_distance < (2*SEG_LENGTH)/3:
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
        if turn_distance < SEG_LENGTH/3:
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
        if self.from_distance < SEG_LENGTH/3:
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
        if turn_distance < SEG_LENGTH/3:
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

class DestinationNode():
    def __init__(self, x, y):
        self.x = x
        self.y = y

