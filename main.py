import os
import sys
import pygame  # main lib for rendering
from world import *
import utility
import math


class Geometry_dash:

    def __init__(self, map_name="Trial.json"):
        #center the window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    


        # screen init
        pygame.init()
        self.FULL_SCREEN_SIZE = utility.get_fullscreen()
        self.last_screen_size = utility.BASE_SIZE
        self.window = pygame.display.set_mode(utility.BASE_SIZE, pygame.RESIZABLE)
        self.display = pygame.Surface(utility.BASE_SIZE)
        pygame.display.set_caption('Geometry Dash')


        #timing
        self.clock = pygame.time.Clock()
        self.max_fps = 60  #tick rate
        self.dt = 0

        #making of the player
        self.player = pygame.Rect(200, 450, 30,30)  # x, y, w, h ---> this is the hitbox of the player, not the actual image. The image will be drawn based on this rect, but can be rotated and scaled independently.
        self.Player_rect = self.player.copy()  # This will be used for drawing the rotated image and collision detection
        self.player_imgs = utility.SpriteSheet()
        self.player_imgs.extract_single_image("player_sprites/Simple_cube.jpg", self.player.size, 255, convert_alpha=False)  # Load the player image and set its size to match the player's hitbox. Set convert_alpha to False since the image doesn't have transparency.
        self.rotation = 0
        self.rotation_to = 0
        self.GRAVITY = -9.8  # all caps = constant
        self.velocity = pygame.Vector2(0, 0)
        self.mass = 5
        self.jump = False
        self.jump_height = 8
        self.mode = "Cube"

        #background
        self.ground = pygame.Rect(0, 480, 1200, 800)
        self.bg = utility.SpriteSheet()
        self.bg.extract_single_image("Textures/bg.jpg", (utility.BASE_SIZE[0],utility.BASE_SIZE[1]), 255)
        self.bg_scroll = 0
        self.bg_scroll_2 = utility.BASE_SIZE[0]
        self.bg_hue = 0
        self.speed = 700
        self.tint_surface = pygame.Surface(utility.BASE_SIZE, pygame.SRCALPHA)
        #Editor
        self.world = Editor(
            [[3,0,0,4]], True, self.ground.y, self.display
        )  
        self.world.reset()

        self.world.load_from_dict(utility.load_map(map_name))

        self.debug = True #for hitbox
        self.Text_debug = False #for console logs

    def run(self):
        while True:
            # Calculate scaling
            window_w, window_h = self.window.get_size()
            base_h = utility.BASE_SIZE[1]
            
            if window_h == 0: window_h = 1
            scale = window_h / base_h
            logical_w = int(window_w / scale)
            logical_h = base_h

            if self.display.get_width() != logical_w or self.display.get_height() != logical_h:
                if (self.display.get_width(), self.display.get_height()) != self.FULL_SCREEN_SIZE: self.last_screen_size = (self.display.get_width(), self.display.get_height()) 
                self.bg.rezize_images((logical_w, logical_h))
                self.display = pygame.Surface((logical_w, logical_h))
                self.tint_surface = pygame.Surface((logical_w, logical_h), pygame.SRCALPHA)
                self.ground.width = logical_w
                self.world.screen = self.display
                

            # Mouse correction
            mx, my = pygame.mouse.get_pos()
            mouse_pos = (mx / scale, my / scale)

            self.display.fill((116, 75, 196))  #rgb - 255-0
            self.dt = self.clock.tick(60) / 1000  # the number inside is the fps or will also tick rate
            # draw stuff
            self.draw(mouse_pos)
            #update physics or level editor
            if not self.world.editor:
                self.apply_player_physics()
            else:
                move_type = self.world.level_editor(mouse_pos)
                if move_type[0]: self.player.move_ip(0, self.world.grid);self.ground.move_ip(0, self.world.grid)  # up
                if move_type[1]: self.player.move_ip(0, -self.world.grid);self.ground.move_ip(0, -self.world.grid)  # down
                if move_type[2]: self.player.move_ip(self.world.grid, 0)  # left
                if move_type[3]: self.player.move_ip(-self.world.grid, 0)  # right
                

            collide = self.world.update_world(
                self.world.grid * 10 * self.dt, self.player,
                self.debug)
            
            if collide and not self.debug:
                self.player.topleft = (200, 450)
                self.world.reset()
                self.velocity.y = 0
                self.rotation = 0

            #event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.world.change_place_type(event) #update the block type to be placed in the editor

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_F3:
                        self.debug = not self.debug
                    if event.key == pygame.K_F4:
                        self.Text_debug = not self.Text_debug
                    if event.key == pygame.K_F2:
                        self.world.editor = not self.world.editor
                        self.world.reset()  # Reset camera scroll when toggling editor mode
                        self.player.topleft = (200, 450)  # Reset player position when toggling editor mode
                        self.ground.topleft = (0, 480)  # Reset ground position when toggling editor mode
                    if event.key == pygame.K_r and (event.mod & pygame.KMOD_CTRL):
                      
                        self.player.topleft = (200, 450)  # Reset player position when toggling editor mode
                        self.ground.topleft = (0, 480)  # Reset ground position when toggling editor mode
                        self.world.set_level([[3,0,0,4]])

                    if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                        data = self.world.__dict__()
                        utility.save_map("Trial.json", data)

                    if event.key == pygame.K_F11:
                        if utility.get_fullscreen() == self.FULL_SCREEN_SIZE:
                            self.screen = pygame.display.set_mode(utility.BASE_SIZE, pygame.RESIZABLE)
                        else:
                            self.screen = pygame.display.set_mode(self.FULL_SCREEN_SIZE)

                        

                if event.type == pygame.VIDEORESIZE: # Updated to VIDEORESIZE for modern pygame
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Render to window
            scaled_display = pygame.transform.scale(self.display, (window_w, window_h))
            self.window.blit(scaled_display, (0, 0))

            pygame.display.update()
            if self.Text_debug:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(self)
                print(self.world)
                print(collide)

    def draw(self, mouse_pos):
        # DRAW ORDER:
        # 1. Background (already filled with color)
        # 2. World (blocks and spikes)
        # 3. Ground (drawn before player so player can go behind it)
        # 4. Player (drawn after ground so it can go behind it)

        # Update background tint
        color = pygame.Color(255, 255, 255)
        if not self.world.editor:
            color = pygame.Color(255, 255, 255)
            self.bg_hue = (self.bg_hue + 10 * self.dt) % 360
            color = pygame.Color(0)
            color.hsva = (self.bg_hue, 70, 100, 100)
            
        bg_img = self.bg.get_image(0)
        # draw background
        self.display.blit(bg_img, (self.bg_scroll, 0))
        self.display.blit(bg_img, (self.bg_scroll_2, 0))
        if not self.world.editor:
            self.bg_scroll -= self.speed * self.dt
            self.bg_scroll_2 -= self.speed * self.dt
            
            bg_width = bg_img.get_width()
            if self.bg_scroll <= -bg_width:
                self.bg_scroll = self.bg_scroll_2 + bg_width
            if self.bg_scroll_2 <= -bg_width:
                self.bg_scroll_2 = self.bg_scroll + bg_width
            
            # Apply tint
            self.tint_surface.fill(color)
            self.display.blit(self.tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
        pygame.draw.rect(self.display, "dark green", self.ground)

    

        #draw plaeyer
        self.display.blit(self.player_imgs.get_image(0), self.Player_rect if not self.world.editor else self.player)  

        #draw UI and debug info
        if self.debug:
            pos = pygame.Vector2(mouse_pos) + pygame.Vector2(self.world.x_scroll, self.world.y_scroll)
            utility.render_text(f"FPS: {round(self.clock.get_fps())}", (10, 10), 20, surface=self.display)
            utility.render_text(f"Player: {self.player}", (10, 30), 20, surface=self.display)
            utility.render_text(f"Mouse: {pos}", (10, 70), 20, surface=self.display)
            utility.render_text(f"Mouse Grid: ({(pos.x // self.world.grid) * self.world.grid}, {(pos.y // self.world.grid) * self.world.grid})", (10, 90), 20, surface=self.display)
            utility.render_text(f"Image Size: {self.player_imgs.get_image(0).get_size()}",(10, 50), 20, surface=self.display)
            pygame.draw.rect(self.display, (255, 0, 0), self.player, 2)
            if not self.world.editor:pygame.draw.rect(self.display, (255, 0, 255), self.Player_rect, 2)    
  
        
        

    def apply_player_physics(self):

        #update player first
        self.player.move_ip(self.velocity)

        #gravity bool
        
        
        #grav implementation
        self.velocity.y -= self.GRAVITY * self.mass * self.dt
        self.velocity.y = min(self.velocity.y, 50)

        #ground colliton
        if self.player.colliderect(self.ground):  # rect vs rect: if collide => True no collide => False
            self.jump = True
            self.rotation = 0
            self.velocity.y = 0
            self.player.y = (self.ground.y - self.player.h)
        
        on_cube, level, dead = self.world.cube_collition(self.player, self.velocity.y) # Check collision with the world using the rotated hitbox
        if dead and not self.debug: 
            self.player.topleft = (200, 450)
            self.world.reset()
            self.velocity.y = 0
            self.rotation = 0 # If collided with a cube kill_zone, exit the game
        if on_cube:
            self.rotation_to = self.rotation - self.rotation_to % 45 #Smooths the cube to an angle of 90 degrees
            self.jump = True #FIX UT GAME
            if self.rotation != self.rotation_to:
                if self.rotation_to % 90 == 0:
                    self.rotation -= 1
                else:
                    self.rotation += 1
            self.rotation = 0
            self.velocity.y = 0
            if level is not None:
                self.player.y = level - self.player.h  # Align player with the top of the block
                


       

        #update player rotation and everything else
         #draw player
        #add rotation to player
        if not self.jump:
            self.rotation = (self.rotation - 600 * self.dt) % 360
        self.player_imgs.images[0] = pygame.transform.rotate(
            self.player_imgs.original_image[0], self.rotation)

        #Key the Black Pixels of the Player
        self.player_imgs.original_image[0].set_colorkey((0, 0, 0))

        # Center the Rotated Image on the Player's Hitbox
        shift = self.player_imgs.get_image(0).get_rect()
        x = self.player.x - (shift.w - self.player.w) / 2
        y = self.player.y - (shift.h - self.player.h) / 2
        self.Player_rect = pygame.Rect(x, y, shift.w, shift.h)



        if self.jump and (pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_UP] or pygame.mouse.get_pressed()[0]):
            self.velocity.y -= self.jump_height * 100 * self.dt
            self.jump = False

    

    def __str__(self):
        return f"""
        Vel: {self.velocity}
        Dt: {self.dt}
        Can Jump: {self.jump}
        OS: {os.name}
        Cube Rotation: {math.sin(self.rotation):.3f}
        """


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear') #reset console on start
    app = Geometry_dash(map_name = "Trial.json")
    app.run()
