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
pygame.display.set_caption("Space Invaders, REDUX5")

# Load images and assets

# Ships
RED_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_blue_small.png"))
PLAYER_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "Player_SpaceShip_01.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))

# Powerups
HEALTH_UP = pygame.image.load(os.path.join("assets", "Heart_Powerup.png"))

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
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # Increment the laser object's 'y' value by the 'velocity' argument
    def move(self, velocity):
        self.y += velocity

    # Returns True or False depending on the position of the laser object.  If the object
    # is off of the visible screen, return True
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

# Parent class: 'Ship'
class Ship:

    # Class Variables
    ################
    LASER_SOUND_EFFECT = pygame.mixer.Sound(os.path.join("assets\laser-gun-19sf.mp3"))
    LASER_SOUND_EFFECT.set_volume(.2)

    # Cooldown will be equal to a quarter second (FPS/2)
    COOLDOWN = 25

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
                player_hit_sound = pygame.mixer.Sound(os.path.join("assets\mixkit-small-hit-in-a-game-2072.wav"))
                player_hit_sound.set_volume(.4)
                player_hit_sound.play()
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):

        # Create a new Laser object and append it to the object's 'lasers' list, then increment 'cool_down_counter' by one
        # so that not too many Laser objects can be created close together
        if self.cool_down_counter == 0:
            if self.y > 0:
                laser = Laser(self.x, self.y, self.laser_img)
                self.lasers.append(laser)
                self.LASER_SOUND_EFFECT.play()
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
class playerShip(Ship):

    # Class Variables
    #################

    # The laser sound effect that the player ship object will use
    LASER_SOUND_EFFECT = pygame.mixer.Sound(os.path.join("assets\laser-gun-19sf.mp3"))
    LASER_SOUND_EFFECT.set_volume(.2)
    
    player_velocity = 3.5
    lives = 5
    score = 0

    # Class Methods
    ###############

    def __init__(self, x, y, health=100):

        # Call the parent constructor 'Ship'
        super().__init__(x, y, health)

        self.ship_img = PLAYER_SPACE_SHIP
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
                        self.score += 1
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        
    def shoot(self):

        # Create a new Laser object and append it to the object's 'lasers' list, then increment 'cool_down_counter' by one
        # so that not too many Laser objects can be created close together
        if self.cool_down_counter == 0:
            if self.y > 0:
                laser1 = Laser(self.x + 30, self.y - 8, self.laser_img)
                laser2 = Laser(self.x - 35, self.y - 8, self.laser_img)
                self.lasers.append(laser1)
                self.lasers.append(laser2)
                self.LASER_SOUND_EFFECT.play()
                self.cool_down_counter += 1
        
    def spawn_player(x, y):
        player_ship = playerShip(x, y)
        return player_ship
                        
    def get_health(self):
        return self.health
    
    def set_health(self, health):
        self.health = health
        
    def get_lives(self):
        return self.lives

    def set_lives(self, lives):
        self.lives = lives

# Child class: 'EnemyShip' inherits from parent class 'Ship
class enemyShip(Ship):

    # Class Variables
    LASER_SOUND_EFFECT = pygame.mixer.Sound(os.path.join("assets\laser.mp3"))
    LASER_SOUND_EFFECT.set_volume(.2)
    
    ENEMY_VELOCITY = 1.6

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

# Child class: 'Powerup' inherits from parent class 'Ship'
class Powerup(Ship):
    
    # Class variables
    VELOCITY = 2.5
    
    def __init__(self, x, y, health=1):
        super().__init__(x, y, health)

# Child class: 'HealthPowerup' inherits from parent class 'Powerup'; (Grandchild of 'Ship')
class healthPowerup(Powerup):
    
    def __init__(self, x, y, health=1):
        super().__init__(x, y, health)
        self.ship_img = HEALTH_UP
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def check_collision(self, obj):
        if super().check_collision(obj):
            obj.health = 100
        return super().check_collision(obj)
        
    def move(self, velocity):
        self.y += velocity
        
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


def display_healthbar(window, health, player_ship):
    health_rect = pygame.Rect(player_ship.x, (player_ship.y + 110), health, 10)
    lost_health_rect = pygame.Rect(player_ship.x, (player_ship.y + 110), 100, 10)
    pygame.draw.rect(window, (255, 0, 0), lost_health_rect)
    pygame.draw.rect(window, (0, 255, 0), health_rect)

def display_score(window, score):
    score_font = pygame.font.SysFont("onyx", 30)
    score_label = score_font.render(f"Score: {score}", 1, (255, 255, 255))
    window.blit(score_label, (10, 40))
    return score_label

def display_high_score(window, high_score):
    high_score_font = pygame.font.SysFont("onyx", 30)
    high_score_label = high_score_font.render(f"High Score: {high_score}", 1, (132, 233, 229))
    window.blit(high_score_label, (WIDTH - high_score_label.get_width() - 10, 40))
    

# Function main(): Function contains logic for running the main game
def main():

    # Game variables
    ################

    run = True
    FPS = 60  # Try to keep this at 60 or above, otherwise the game will update less frequently
    clock = pygame.time.Clock()
    level = 0 
    game_over_count = 0
    main_font = pygame.font.SysFont("onyx", 30)
    game_over_font = pygame.font.SysFont("onyx", 50)
    pause_game_font = pygame.font.SysFont("onyx", 50)
    played_game_over_sound = False
    enemies = []
    powerups = []
    enemy_wave_length = 0
    player_ship = playerShip.spawn_player(375, 650)
    
    if os.path.exists("space_invaders_score.txt"):
        high_score_file = open("space_invaders_score.txt", "r", 1)
        high_score_list = high_score_file.readlines()
        high_score = int(high_score_list[0])
        high_score_file.close()
        high_score_file = open("space_invaders_score.txt", "w", 1)
        
    else:
        high_score_file = open("space_invaders_score.txt", "w", 1)
        high_score = 0
    
    # Method redraw_window(): (0 arguments) This function will update the window by redrawing the background
    def redraw_window():

        # Render the background
        WIN.blit(BACKGROUND, (0, 0))

        # Initialize text; color: (255,255,255) == white
        lives_label = main_font.render(f"Lives: {player_ship.lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        # Render text to display
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Render the score to display
        display_score(WIN, player_ship.score)
        
        # Render the high score to displa
        display_high_score(WIN, high_score)
       
        # Render the health bar to display
        display_healthbar(WIN, player_ship.health, player_ship)

        # Render the powerups to display
        for powerup in powerups:
            powerup.draw_ship(WIN)
            
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
        
    def game_over(health, lives):
        
        if (health <= 0) or (lives == 0):
            
            nonlocal played_game_over_sound
            nonlocal game_over_count
            
            game_over_count += 1
            
            game_over_label = game_over_font.render(
                f"GAME OVER", 1, (255, 0, 0))
            WIN.blit(game_over_label, (WIDTH/2 -
                        game_over_label.get_width()/2, 375))
            pygame.display.update()
        
            if played_game_over_sound == False:
                    game_over_sound_effect = pygame.mixer.Sound(os.path.join(
            "assets\mixkit-arcade-fast-game-over-233.wav"))
                    played_game_over_sound = True
                    game_over_sound_effect.play()
                    time.sleep(1)
                    game_over_sound_effect.stop()
            return True
    
        else:
            return False
        
    def next_level(level, enemies_list, enemy_wave_length, window):
        if len(enemies_list) == 0:
            
            level += 1
            
            if level < 3:
                enemy_wave_length += 5
            else:
                enemy_wave_length += 3
            
            if level % 3 == 0:
                health_heart = healthPowerup(random.randrange(100, WIDTH - 100), -20, None)
                powerups.append(health_heart)
            
            for enemy in range(enemy_wave_length):
                enemy = enemyShip(random.randrange(
                    50, WIDTH-50), random.randrange(-1000, -100), random.choice(["red", "blue", "green"]))
                enemies_list.append(enemy)
        
        return level, enemies_list, enemy_wave_length
    

    # RUN GAME
    ##########

    # While loop runs the game logic until the user quits
    while run == True:

        clock.tick(FPS)
        redraw_window()  # Update the window on every frame
        
        # Game over check
        ##################
        
        # If the user runs out of lives or player health hits 0, exit the game logic loop (player loses, exit the game)
        if game_over(player_ship.get_health(), player_ship.get_lives()):
            
            # Wait 3 seconds
            if game_over_count > FPS * 2:
                run = False
            else:
                continue
        
        # Next level check
        ##################
        
        # Increment the 'level' by one every time all enemies are eliminated
        level, enemies, enemy_wave_length = next_level(level, enemies, enemy_wave_length, WIN)

        # Check for user quitting the game, or exiting the window
        for event in pygame.event.get():

            if event.type == pygame.QUIT:  # If the user quits, then set 'run' flag to False to exit game run loop
                player_ship.score = 0
                run = False

            # Display the coordinates of the mouse position each time the user clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Mouse cursor is at " + str(pygame.mouse.get_pos()))

        # Create a dictionary that will map keys pressed to a True or False value
        keys = pygame.key.get_pressed()

        # Player movement; player cannot move off of the screen at all

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

        # TEST
        if (keys[pygame.K_h]):
            print(high_score_file.readline())
            print(high_score_file.read())
            print(high_score)
            
            
        # Shoot lasers
        if keys[pygame.K_SPACE]:
            player_ship.shoot()
            
        # Pause game
        if keys[pygame.K_ESCAPE]:
            pause_game(keys)

        # Check powerup collision with player
        for powerup in powerups:
            
            # Check for player collision with a powerup
            if(powerup.check_collision(player_ship)):
                if(isinstance(powerup, healthPowerup)):
                    health_collect_sound = pygame.mixer.Sound(os.path.join("assets\mixkit-video-game-health-recharge-2837.wav"))
                    health_collect_sound.set_volume(.4)
                    health_collect_sound.play()
                powerups.remove(powerup)
            
            powerup.move(powerup.VELOCITY)
        
        # Enemy movement
        for enemy in enemies:

            # Check for player colliding with an enemy
            if (player_ship.check_collision(enemy)):
                player_ship.score += 1
                player_crash_sound = pygame.mixer.Sound(os.path.join("assets\mixkit-8-bit-bomb-explosion-2811.wav"))
                player_crash_sound.set_volume(.4)
                player_crash_sound.play()
                player_ship.health -= 30
                enemies.remove(enemy)
            
            # Move enemy by 'enemy_velocity'
            enemy.move(enemy.ENEMY_VELOCITY)

            # Move the lasers that an enemy shoots
            if enemy.random_laser_chance() >= 995:
                enemy.shoot()

            enemy.move_lasers(enemy.laser_velocity, player_ship)

            # If the enemy object reaches the bottom of the screen, remove a life from the player and remove that
            # enemy from the game
            if enemy.y >= 750:
                player_ship.lives -= 1
                enemies.remove(enemy)

        player_ship.move_lasers(player_ship.laser_velocity, enemies)
        
    #(end while loop)
    
    # Set the high score
    if (player_ship.score > high_score):
        
        high_score_file.write(f"{player_ship.score}")
    else:
         high_score_file.write(f"{high_score}")
         high_score_file.close()


main()  # Run the game!
