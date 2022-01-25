import math
import sys
import pygame
import os
import random
import time

pygame.font.init()

# Set up the display
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# The name of the display window will be "Space Invaders"
pygame.display.set_caption("Space Invaders")

# Load images and assets

# Ships
RED_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Classes

# Default parent class: 'Ship'


class Ship:

    # Default constructor
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    # Function draw_ship(window): takes one argument, which is the display that the ship will be
    # rendered onto
    def draw_ship(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Child class: 'PlayerShip' inherits from parent class 'Ship'


class PlayerShip(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER

        # Create a mask that fits the "ship_img" image pixel perfectly for collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health


class EnemyShip(Ship):

    # A dictionary that stores the loaded assets with their corresponding color key (key = color, value = assets tuple)
    COLOR_MAP = {"red": (RED_SPACE_SHIP, RED_LASER),
                 "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                 "blue": (BLUE_SPACE_SHIP, BLUE_LASER)}

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)

        # 'ship_img' will be set to the first value at the 'color' key, and 'laser_img' will be set to the second value at the 'color' key
        # in the 'COLOR_MAP' dictionary
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Function move(velocity): takes one argument 'velocity', which will be added to the EnemyShip's 'y' value.  Since
    # EnemyShip objects will only move towards the player (down), this is the only needed effect
    def move(self, velocity):
        self.y += velocity

#################################################################################################################################

# Function main(): Function contains logic for running the main game


def main():

    run = True
    FPS = 60  # Try to keep this at 60 or above, otherwise the game will update less frequently
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("onyx", 30)
    end_font = pygame.font.SysFont("onyx", 50)
    player_ship = PlayerShip(375, 650)
    player_velocity = 3.5

    enemies = []
    enemy_wave_length = 5
    enemy_velocity = 20

    # Function redraw_window: This function will update the window by redrawing the background
    def redraw_window():

        # Render the background
        WIN.blit(BACKGROUND, (0, 0))

        # Initialize text; color: (255,255,255) == white
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        # Render text to display
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Render the enemies to display
        for enemy in enemies:
            enemy.draw_ship(WIN)

        # Render the player ship to display
        player_ship.draw_ship(WIN)

        pygame.display.update()

    # While loop runs the game logic until the user quits
    while run == True:

        clock.tick(FPS)

        if lives == 0:
            run = False
            break
            
        # Increment the 'level' by one every time all enemies are eliminated
        if len(enemies) == 0:
            level += 1

            # Create 5 new enemies
            enemy_wave_length += 5

            # Render each enemy in a random position
            for i in range(enemy_wave_length):
                enemy = EnemyShip(random.randrange(50, WIDTH-50), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)   
                
         # Check for user quitting the game, or exiting the window
        for event in pygame.event.get():

            if event.type == pygame.QUIT:  # If the user quits, then set 'run' flag to False to exit game run loop
                run = False

            # Display the coordinates of the mouse position each time the user clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Mouse cursor is at " + str(pygame.mouse.get_pos()))

        # Create a dictionary that will map keys pressed to a True or False value
        keys = pygame.key.get_pressed()

        # Player movement logic; player can move up only to a y value of 500, and cannot move off of the screen at all

        # Left (subtract from x value)
        if keys[pygame.K_a] == True and player_ship.x - player_velocity > -13:
            player_ship.x -= player_velocity
        # Down (add to y value)
        if keys[pygame.K_s] == True and player_ship.y + player_velocity < HEIGHT - player_ship.get_height():
            player_ship.y += player_velocity
        # Right (add to x value)
        if keys[pygame.K_d] == True and player_ship.x + player_velocity < WIDTH - player_ship.get_width() + 13:
            player_ship.x += player_velocity
        # Up (subtract from y value)
        if keys[pygame.K_w] == True and player_ship.y - player_velocity > 500:
            player_ship.y -= player_velocity

        for enemy in enemies:
            enemy.move(enemy_velocity)
            if enemy.y >= 750:
                lives -= 1
                enemies.remove(enemy)
        
        redraw_window()  # Update the window on every frame


    game_over_label = end_font.render(f"GAME OVER", 1, (255,0,0))
    WIN.blit(game_over_label, (300,375))
    pygame.display.update()
    time.sleep(2)
    
    
main()  # Run the game!
