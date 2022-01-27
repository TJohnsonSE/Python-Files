from asyncio import events
from json.encoder import INFINITY
import math
import sys
import pygame
import os
import random
import time
import threading

pygame.font.init()
pygame.mixer.init()

# Display and Assets
######################################################################

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
#############################################################################

# Class: 'Laser'


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        # Mask fits snugly to the pixels of the model; needed for accurate collision
        self.mask = pygame.mask.from_surface(self.img)

    # Render the laser object to the display window
    def draw(self, WIN):
        WIN.blit(self.img, (self.x, self.y))

    # Increment the laser object's 'y' value by the 'velocity' argument
    def move(self, velocity):
        self.y += velocity

    # Returns True or False depending on the position of the laser object.  If the object
    # is off of the visible screen, return True
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

# Default parent class: 'Ship'


class Ship:

    # Class Variables
    ################
    laser_sound_effect = pygame.mixer.Sound("laser-gun-19sf.mp3")
    laser_sound_effect.set_volume(.2)

    # Cooldown will be equal to a quarter second (FPS/2)
    COOLDOWN = 20

    # Class Methods
    #################

    # Default Ship constructor

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.laser_velocity = 4

    # Function draw_ship(window): takes one argument, which is the display that the ship will be
    # rendered onto
    def draw_ship(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def draw_lasers(self, window):
        for laser in self.lasers:
            laser.draw(window)

    # Function move_lasers(velocity, obj): takes 2 arguments, 'velocity' is the speed at which Laser objects will travel
    # and 'obj' refers to the object that the method will pass to the 'laser.collision()' method to check for collision between
    # the laser and 'obj'
    def move_lasers(self, velocity, obj):

        self.laser_cooldown()

        for laser in self.lasers:

            # Move the laser object by the 'velocity' argument
            laser.move(velocity)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):

        # Create a new Laser object and append it to the object's 'lasers' list, then increment 'cool_down_counter' by one
        # so that not too many Laser objects can be created close together
        if self.cool_down_counter == 0:
            if self.y > 0:
                laser = Laser(self.x, self.y, self.laser_img)
                self.lasers.append(laser)
                self.laser_sound_effect.play()
                self.cool_down_counter += 1

    def laser_cooldown(self):

        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0

        if self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def check_collision(self, obj):
        return collide(obj, self)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Child class: 'PlayerShip' inherits from parent class 'Ship'


class PlayerShip(Ship):

    # Class Variables
    #################

    # The laser sound effect that the player ship object will use
    laser_sound_effect = pygame.mixer.Sound("laser-gun-19sf.mp3")
    laser_sound_effect.set_volume(.2)
    
    player_velocity = 3.5

    # Class Methods
    ###############

    def __init__(self, x, y, health=100):

        # Call the parent constructor 'Ship'
        super().__init__(x, y, health)

        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER

        # Create a mask that fits the "ship_img" image pixel perfectly for collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # Method move_lasers(velocity, objs): Overridden method of parent 'Ship' class.  This method differs from the parent
    # method in that the velocity passed to the Laser.move() method needs to be negative for the laser to travel upwards.  It
    # also must check for collision with the 'objs' argument, which will generally be a list of enemy ship objects.
    def move_lasers(self, velocity, objs):

        self.laser_cooldown()

        for laser in self.lasers:
            laser.move(-velocity)

            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

# Child class: 'EnemyShip' inherits from parent class 'Ship


class EnemyShip(Ship):

    # Class Variables
    laser_sound_effect = pygame.mixer.Sound("laser.mp3")
    laser_sound_effect.set_volume(.2)
    
    enemy_velocity = 1.6

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

    # Method move(velocity): takes one argument 'velocity', which will be added to the EnemyShip's 'y' value.  Since
    # EnemyShip objects will only move towards the player (down), this is the only needed effect
    def move(self, velocity):
        self.y += velocity

    def random_laser_chance(self):
        random_chance = random.randrange(0, 1000)
        return random_chance

# Program Functions (Global scope)
##################################


def cooldown(self):

    if self.cool_down_counter >= self.COOLDOWN:
        self.cool_down_counter = 0

    if self.cool_down_counter > 0:
        self.cool_down_counter += 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def display_healthbar(window, health):
    pygame.draw.rect(window, (0, 255, 0),
                     ((375 - (3 * health)/2), 10, (3 * health), 10))

##################################################

# Function main(): Function contains logic for running the main game


def main():

    # Game variables
    ################

    run = True
    FPS = 60  # Try to keep this at 60 or above, otherwise the game will update less frequently
    clock = pygame.time.Clock()
    level = 0  # Start at level 0
    lives = 5
    game_over_count = 0
    game_over = False
    main_font = pygame.font.SysFont("onyx", 30)
    game_over_font = pygame.font.SysFont("onyx", 50)
    pause_game_font = pygame.font.SysFont("onyx", 50)
    player_ship = PlayerShip(375, 650)
    game_over_sound_effect = pygame.mixer.Sound(
        "mixkit-arcade-fast-game-over-233.wav")
    played_game_over_sound = False
    enemies = []
    enemy_wave_length = 0

    # Method redraw_window(): (0 arguments) This function will update the window by redrawing the background
    def redraw_window():

        # Render the background
        WIN.blit(BACKGROUND, (0, 0))

        # Initialize text; color: (255,255,255) == white
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        # Render text to display
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Render the health bar to display
        display_healthbar(WIN, player_ship.health)

        # Render the enemies to display
        for enemy in enemies:
            enemy.draw_ship(WIN)
            enemy.draw_lasers(WIN)

        # Render the player ship to display
        player_ship.draw_ship(WIN)
        player_ship.draw_lasers(WIN)

        pygame.display.update()
        
    # Function pause_game: takes one argument, which is a boolean value with a value of 'True' if the escape key is pressed
    # or 'False' if it is not
    def pause_game(keys_dict):

        print("Game paused")
            
        print(f"Escape = {keys[pygame.K_ESCAPE]}")
            
        player_ship.player_velocity = 0
        enemy_velocity = 0

        pause_game_label = pause_game_font.render(
            f"PAUSED", 1, (255, 255, 255))

        WIN.blit(pause_game_label,
                ((WIDTH/2 - pause_game_label.get_width()/2), HEIGHT/2))

        pygame.display.update()
        

    # RUN GAME
    ##########

    # While loop runs the game logic until the user quits
    while run == True:

        clock.tick(FPS)
        redraw_window()  # Update the window on every frame

        # Game over checks
        ##################
        
        # If the user runs out of lives or player health hits 0, exit the game logic loop (player loses, exit the game)
        if lives == 0 or player_ship.health == 0:
            game_over = True
            game_over_count += 1

        # When the player loses
        if game_over:

            # Display game over screen for five seconds (FPS * 3) and exit while loop running the game logic
            game_over_label = game_over_font.render(
                f"GAME OVER", 1, (255, 0, 0))
            WIN.blit(game_over_label, (WIDTH/2 -
                     game_over_label.get_width()/2, 375))
            pygame.display.update()

            if played_game_over_sound == False:
                played_game_over_sound = True
                game_over_sound_effect.play()
                time.sleep(1)
                game_over_sound_effect.stop()

            # Wait 3 seconds
            if game_over_count > FPS * 2:
                run = False
            else:
                continue

        # Increment the 'level' by one every time all enemies are eliminated
        if len(enemies) == 0:
            level += 1

            if level < 3:
                
                # Create 5 new enemies
                enemy_wave_length += 5
            
            else:
                enemy_wave_length += 2
            

            # Render each enemy in a random position
            for i in range(enemy_wave_length):
                enemy = EnemyShip(random.randrange(
                    50, WIDTH-50), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
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

        # Move player_ship left (subtract from x value)
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_ship.x - player_ship.player_velocity > -13:
            player_ship.x -= player_ship.player_velocity

        # Move player_ship down (add to y value)
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player_ship.y + player_ship.player_velocity < HEIGHT - player_ship.get_height():
            player_ship.y += player_ship.player_velocity

        # Move player_ship right (add to x value)
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_ship.x + player_ship.player_velocity < WIDTH - player_ship.get_width() + 13:
            player_ship.x += player_ship.player_velocity

        # Move player_ship up (subtract from y value)
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player_ship.y - player_ship.player_velocity > 0:
            player_ship.y -= player_ship.player_velocity

        # Shoot lasers
        if keys[pygame.K_SPACE]:
            player_ship.shoot()
        # Pause game
        if keys[pygame.K_ESCAPE]:
            pause_game(keys)

        # Enemy movement
        for enemy in enemies:

            if (player_ship.check_collision(enemy)):
                player_ship.health -= 30
                enemies.remove(enemy)
            
            # Move enemy by 'enemy_velocity'
            enemy.move(enemy.enemy_velocity)

            # Move the lasers that an enemy shoots
            if enemy.random_laser_chance() >= 995:
                enemy.shoot()

            enemy.move_lasers(enemy.laser_velocity, player_ship)

            # If the enemy object reaches the bottom of the screen, remove a life from the player and remove that
            # enemy from the game
            if enemy.y >= 750:
                lives -= 1
                enemies.remove(enemy)

        player_ship.move_lasers(enemy.laser_velocity, enemies)


main()  # Run the game!
