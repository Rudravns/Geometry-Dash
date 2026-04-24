import os
import pygame
from world import *
import utility

class Player:
    def __init__(self, world):
        # making of the player
        self.player = pygame.Rect(200, 450, 30, 30)  # x, y, w, h ---> this is the hitbox of the player, not the actual image. The image will be drawn based on this rect, but can be rotated and scaled independently.
        self.Player_rect = self.player.copy()  # This will be used for drawing the rotated image and collision detection
        self.gamemode = "cube"
        self.player_imgs = utility.SpriteSheet()
        self.player_imgs.extract_single_image("player_sprites/Simple_cube.jpg", self.player.size, 255)# Load the player image and set its size to match the player's hitbox. Set convert_alpha to False since the image doesn't have transparency.
        self.rotation = 0
        self.rotation_to = 0
        self.rotation_velocity = 0
        self.rotation_speed = 45
        self.GRAVITY = -1.4  # all caps = constant
        self.velocity = pygame.Vector2(0, 0)
        self.mass = 3.6
        self.jump = False
        self.jump_height = 10.2
        self.air_friction = 0.9
        self.max_fly = 2.4

        start_point = world.get_start_point()
        self.x = start_point.x - world.x_scroll
        self.y = start_point.y + (start_point.height - self.player.height)
        self.Player_rect = self.player.copy()
    
    def check_gamemode(self, world, ground, debug, dt):
        # update player first
        self.player.move_ip(0, self.velocity.y*dt*100)  # move the player based on its velocity. We multiply by dt to make the movement frame rate independent, and by 100 to convert from seconds to milliseconds since pygame's clock works in milliseconds.

        if self.gamemode == "cube":
            self.GRAVITY = -1.4
            self.mass = 3.6
            self.cube_physics(world, ground, debug, dt)
        elif self.gamemode == "ship":
            self.GRAVITY = -0.8
            self.mass = 2.4
            self.ship_physics(world, ground, debug, dt)
    
    def cube_physics(self, world, ground, debug, dt):
        # Check if level ended or not
        if not world.editor or not debug:
            if world.end(self.player):
                #exit()
                pass

        # grav implementation
        self.velocity.y -= self.GRAVITY * self.mass * dt * 10
        #self.velocity.y = min(self.velocity.y, 20)
        #self.velocity.y = np.lerp(self.velocity.y, -self.jump_height, 0.5)

        # ground colliton
        self.player.y += 1 #Move player down 1 pixel to check if it's colliding with the ground or cubes
        if self.player.colliderect(ground):  # rect vs rect: if collide => True no collide => False
            self.jump = True
            #self.rotation = 0
            self.velocity.y = 0
            self.player.y = (ground.y - self.player.h)
        else: self.jump = False

        on_cube, level, dead = world.cube_collition(self.player, self.velocity.y)  # Check collision with the world using the rotated hitbox
        if dead and not debug:
           return True
        if on_cube:
            self.jump = True

            self.velocity.y = 0
            if level is not None:
                self.player.y = level - self.player.h  # Align player with the top of the block

        # update player rotation and everything else
        # draw player
        # add rotation to player
        if self.jump:
            if pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_UP] or pygame.mouse.get_pressed()[0]:
                self.velocity.y = -self.jump_height
                #self.velocity.y = np.lerp(self.velocity.y, -self.jump_height, 0.5)
                self.jump = False
            else:
                if self.rotation_velocity > 0:
                    self.smooth_rotation(self.rotation > self.rotation_to, dt)
                else:
                    self.smooth_rotation(self.rotation < self.rotation_to, dt)
        else:
            self.rotation = (self.rotation - self.rotation_speed * 10 * dt) % 360  # here it was 600 before which does a full 360  also we do mod 360 so it doesn't go above 360 deg
            self.rotation_to = self.rotation - self.rotation % 90  # In floor terms, subtracts rotation to the nearest floor of 90 degree angle
            if self.rotation % 90 != self.rotation % 45: self.rotation_to += 90  # If the rotation is closer to the next 90 degree angle, rotate to that one instead

            if self.rotation > self.rotation_to:
                self.rotation_velocity = -1 * self.rotation_speed
            else:
                self.rotation_velocity = self.rotation_speed
        """ Works only on top of a cube not ground just copy the code from cube and paste it here for ONLY ROTATION"""

    def rotate(self):
        self.player_imgs.images[0] = pygame.transform.rotate(
            self.player_imgs.original_image[0], self.rotation)

        # Key the Black Pixels of the Player
        self.player_imgs.images[0].set_colorkey((0, 0, 0))

        # Center the Rotated Image on the Player's Hitbox
        shift = self.player_imgs.get_image(0).get_rect()
        x = self.player.x - (shift.w - self.player.w) / 2
        y = self.player.y - (shift.h - self.player.h) / 2
        self.Player_rect = pygame.Rect(x, y, shift.w, shift.h)

    def ship_physics(self, world, ground, debug, dt):
        self.velocity.y -= (self.mass * self.GRAVITY * dt * 10) * self.max_fly
        if pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_UP] or pygame.mouse.get_pressed()[0]:
            self.velocity.y += (self.mass * self.GRAVITY * dt * 10) * (self.max_fly * 2)
        self.velocity.y = self.velocity.y * self.air_friction


    def smooth_rotation(self, condition, dt):
        """
        :condition: bool
        """

        if condition:
            pass
        else:
            self.rotation = self.rotation_to
            return

        self.rotation_to += self.rotation_velocity * self.rotation_speed * dt
        if self.rotation_velocity > 2: self.rotation_velocity = self.rotation_velocity * 0.9
        else: self.rotation_velocity = 2
        #print("smooth")

    def debug_draw(self, y, screen):
        utility.render_text(f"Rotation: {self.rotation:.2f}", (10, y), 20, surface=screen)
        utility.render_text(f"Rotation To: {self.rotation_to:.0f}", (10, y + 20), 20, surface=screen)
        utility.render_text(f"Jump: {self.jump}", (10, y + 40), 20, surface=screen)
        utility.render_text(f"Velocity: {self.velocity.y:.2f}", (10, y + 60), 20, surface=screen)
        return y + 20 * 4 # 20 is space between lines, 4 is the number of lines