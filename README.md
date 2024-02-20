# Snake #

My take on the classic "Snake" game, using the Pygame Library

## Controls ##

Use the arrow keys to move the head of the snake.

Press spacebar to pause or unpause the game

## Objectives ##

Avoid making contact with any of your body segments, the edges of the screen, or with SpikeBalls!

Touching the head of the snake to a piece of food will increase your score, but also increase your body length.

Different food types will have different effects:

- Red Apples: Normal food, gives you points equal to the level you have reached.
- Green Melons: Triple points!
- Yellow Lemons: Golden Glow! Gives you double the points for the next food you eat.
- Blue Blueberry: Shield Food. Grants you a shield which will protect you from the next collision with a SpikeBall
- Purple Grapes: Slow Food. Slows you down, making it easier to maneuver the snake.
- Pink Mystery Box: Has a variety of random effects. Try it and see!

Eating enough food will increase the level, resulting in more points, but also more danger!

Have fun!

## Installing Requirements With a Virtual Environment ##

To install the requirements to run this program, do the following:

### Mac/Linux ###

- Open a Terminal window
- Navigate to the directory containing the SnakeGame.py file
- Enter the following commands:
  - python3 -m venv .venv
  - source .venv/bin/activate
  - python3 -m pip install --upgrade pip
  - python3 -m pip install -r requirements.txt
- Once you are done, you can leave the virtual environment by the command:
  - deactivate

### Windows ###

- Open a Command Prompt window
- Navigate to the directory containing the SnakeGame.py file
- Enter the following commands:
  - py -m venv .venv
  - .venv/Scripts/activate
  - py -m pip install --upgrade pip
  - py -m pip install -r requirements.txt
- Once you are done, you can leave the virtual environment by the command:
  - deactivate
