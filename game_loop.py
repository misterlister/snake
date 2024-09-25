import pygame as pg
import os
from constants import (
    DIS_WIDTH,
    DIS_HEIGHT,
    HEADER_HEIGHT,
    LINE_WIDTH,
    CLOCK_SPEED,
    RED_COL,
    BLACK_COL,
    WHITE_COL,
    GREEN_COL,
    YELLOW_COL,
    BACKGROUND_COL,
    HEADER_COL,
    MESSAGE_BAR_COL,
    SHADOW_OFFSET,
    COLLISION_RADIUS,
    SAVE_FILE_NAME,
    Direction,
    FoodNum
)
from player import Player
from snake import Snake
    

def gameLoop():
    
    pg.init()
    dis=pg.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
    pg.display.update()
    pg.display.set_caption("Snake!")
    clock = pg.time.Clock()
    
    fonts = make_fonts()
    
    game_over = False
    game_close = False
    game_paused = False

    snake = Snake(dis)
    player = Player(snake, dis, fonts)

    start_screen(dis, fonts)

    while not game_close:
        while game_over == True:
            dis.fill(BLACK_COL)
            display_text("Game Over! Press any key to continue", RED_COL, dis, fonts)
            player.print_score()
            pg.display.update()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_over = False
                    game_close = True
                if event.type == pg.KEYDOWN:
                    write_scores(player, dis, fonts, clock)
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
            pause_text("- Game Paused -", dis, fonts)
            pg.display.update()
        else:    
            dis.fill(BACKGROUND_COL)
            header_bar(dis)
            message_bar(dis)
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
            player.update_durations()
            player.print_message()
            pg.display.update()
            for spikeball in player.spikeballs:
                if spikeball.collide(snake, COLLISION_RADIUS):
                    if snake.shields > 0:
                        snake.shields -= 1
                        player.spikeballs.remove(spikeball)
                    else:
                        game_over = True
            for i in range(len(player.foods)):
                if player.foods[i].collide(snake, COLLISION_RADIUS):
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
        clock.tick(CLOCK_SPEED)

    pg.quit()
    quit()
    
def make_fonts():
    default_font = pg.font.get_default_font()
    heading_font = "bahnschrift"
    message_font = "comicsansms"
    if heading_font not in pg.font.get_fonts():
        heading_font = default_font

    if message_font not in pg.font.get_fonts():
        message_font = default_font

    fonts = {
        "font_style": pg.font.SysFont(heading_font, 40),
        "title_font": pg.font.SysFont(heading_font, 85),
        "high_score_font": pg.font.SysFont(heading_font, 45),
        "pause_font": pg.font.SysFont(heading_font, 85),
        "score_font": pg.font.SysFont(message_font, 30),
        "header_font": pg.font.SysFont(message_font, 35),
        "message_font": pg.font.SysFont(message_font, 35)
    }
    return fonts

def start_screen(dis, fonts):
    play = False
    while not play:
        dis.fill(BLACK_COL)
        title_banner(dis, fonts)
        display_text("Press P-Play, S-See High Scores, Q-Quit Game", WHITE_COL, dis, fonts)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    score_screen(dis, fonts)
                if event.key == pg.K_p:
                    play = True
                if event.key == pg.K_q:
                    pg.quit()
                    quit()

def score_screen(dis, fonts):
    done = False
    while not done:
        dis.fill(BLACK_COL)
        print_scores(dis, fonts)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                done = True


def display_text(msg, colour, dis, fonts):
    msg_text = fonts["font_style"].render(msg, True, colour)
    msg_rect = msg_text.get_rect(center=dis.get_rect().center)
    dis.blit(msg_text, msg_rect)

def pause_text(text, dis, fonts):
    shadow = fonts["pause_font"].render(text, True, BLACK_COL)
    to_print = fonts["pause_font"].render(text, True, RED_COL)
    shadow_rect = shadow.get_rect(center=dis.get_rect().center)
    shadow_rect = shadow_rect.move(SHADOW_OFFSET, SHADOW_OFFSET)
    msg_rect = to_print.get_rect(center=dis.get_rect().center)
    dis.blit(shadow, shadow_rect)
    dis.blit(to_print, msg_rect)

def header_bar(dis):
    # Draw header box
    header_rect = pg.Rect(0, 0, DIS_WIDTH, HEADER_HEIGHT)
    # Fill header box with colour
    pg.draw.rect(dis, HEADER_COL, header_rect)
    # Draw boundary line
    pg.draw.line(dis, BLACK_COL, (0, HEADER_HEIGHT-LINE_WIDTH), (DIS_WIDTH, HEADER_HEIGHT-LINE_WIDTH), LINE_WIDTH)
    
def message_bar(dis):
    # Draw message bar
    msg_rect = pg.Rect(0, HEADER_HEIGHT, DIS_WIDTH, HEADER_HEIGHT)
    # Fill message bar with colour
    pg.draw.rect(dis, MESSAGE_BAR_COL, msg_rect)
    # Draw boundary line
    pg.draw.line(dis, BLACK_COL, (0, HEADER_HEIGHT * 2 - LINE_WIDTH), (DIS_WIDTH, HEADER_HEIGHT * 2 - LINE_WIDTH), LINE_WIDTH)

def title_banner(dis, fonts):
    msg_text = fonts["title_font"].render("Snake!", True, GREEN_COL)
    msg_rect = msg_text.get_rect(midtop=(DIS_WIDTH *1/2, DIS_HEIGHT*1/6))
    dis.blit(msg_text, msg_rect)

def print_scores(dis, fonts):
    banner = fonts["high_score_font"].render("High Scores:", True, GREEN_COL)
    f = open(SAVE_FILE_NAME, "r")
    score_list = f.readlines()
    banner_rect = banner.get_rect(midtop=(DIS_WIDTH *1/2, DIS_HEIGHT*1/15))
    score_renders = []
    score_rects = []
    dis.blit(banner, banner_rect)
    while (len(score_list) > 10):
        score_list.pop()
    for i in range (0, len(score_list)):
        score_list[i] = score_list[i][:-1]
        score_renders.append(fonts["score_font"].render(f"Rank {i+1}:    {score_list[i]}", True, YELLOW_COL))
        score_rects.append(score_renders[i].get_rect(midtop=(DIS_WIDTH *1/2, (DIS_HEIGHT*i/(15))+ DIS_HEIGHT/5)))
        dis.blit(score_renders[i], score_rects[i])
    f.close()

def get_name(player, dis, fonts, clock):
    title_text = fonts["high_score_font"].render("You got a High Score! Enter your name:", True, GREEN_COL)
    title_rect = title_text.get_rect(midtop=(DIS_WIDTH *1/2, DIS_HEIGHT*1/6))
    user_text = ""
    input_rect = pg.Rect(DIS_WIDTH/3, DIS_HEIGHT/2, DIS_WIDTH/4, DIS_HEIGHT/15)
    done = False
    while not done:
        dis.fill(BLACK_COL)
        pg.draw.rect(dis, YELLOW_COL, input_rect)
        text_surface = fonts["font_style"].render(user_text, True, BLACK_COL)
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

def write_scores(player, dis, fonts, clock):
    if not os.path.isfile(SAVE_FILE_NAME):
        with open(SAVE_FILE_NAME, "w"):
            pass
    f = open(SAVE_FILE_NAME, "r")
    score_list = f.readlines()
    f.close()
    score_dict = {}
    add_score = False
    if len(score_list) > 0:
        for entry in score_list:
            words = entry.split()
            player_name = " ".join(words[:-1])
            player_score = words[-1]
            score_dict[player_name] = int(player_score)
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
    user_name = get_name(player, dis, fonts, clock)
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
    f = open(SAVE_FILE_NAME, "w")
    for record in score_dict:
        f.write(f"{record}    {score_dict[record]}\n")
    f.close()
    score_screen(dis, fonts)