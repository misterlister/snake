from enum import IntEnum
import os.path

class FoodNum(IntEnum):
    # number keys for each type of food
    GLOW = 1
    SLOW = 2
    BONUS = 3
    MYSTERY = 4
    SHIELD = 5
    NORMAL = 0

class Direction(IntEnum):
    UP = 0
    DOWN = 180
    LEFT = 90
    RIGHT = 270

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
SPRITES_DIR = os.path.join(MAIN_DIR, "sprites")

BLACK_COL = (0, 0, 0) # colour for snake
BACKGROUND_COL = (205, 225, 255) # colour for the main background screen
GREEN_COL = (0, 155, 0) # colour for normal food
RED_COL = (255, 0, 0) # colour for game over text
WHITE_COL = (255, 255, 255) # colour for the background of the game over screen
YELLOW_COL = (255, 215, 0) # colour for score and food effect text
LEVEL_ALERT_COL = (255, 80, 225) # colour for level up alert colour
HEADER_COL = (0, 0, 150) # colour for the header background
MESSAGE_BAR_COL = (0, 100, 100) # colour for the message header background
TRANSPARENT = (69, 69, 69) # colour to be used for transparency

DIS_WIDTH = 1280
DIS_HEIGHT = 920

HEADER_HEIGHT = 55
LINE_WIDTH = 3

PLAY_HEIGHT = DIS_HEIGHT-HEADER_HEIGHT*2

CLOCK_SPEED = 40

SPRITE_SCALE = 1.25
SEG_LENGTH = 20 * SPRITE_SCALE
START_SPEED = 4
MIN_SPEED = 3
# How many food objects will spawn
NUM_FOOD = 3

MESSAGE_DURATION_MAX = 90
LEVEL_GLOW_DURATION_MAX = 40
LEVEL_GLOW_GRADIENT_DURATION = 15

BLINDNESS_TIME_MAX = 750
BLINDNESS_TIME_PHASE = BLINDNESS_TIME_MAX / 10

TAIL_RADIUS = 1/2 * SEG_LENGTH
COLLISION_RADIUS = 3/4 * SEG_LENGTH
SAFE_RADIUS = 5 * SEG_LENGTH

# rate at which speed changes when eating speed changing food
SPEED_INC = 1/2

SAVE_FILE_NAME = "highscores.txt"

SHADOW_OFFSET = 2

