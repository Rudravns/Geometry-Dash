import os
import sys
import pygame # main lib for rendering
from world import *
import utilies

class Geometry_dash:

    def __init__(self):

        # screen init
        pygame.init()
        self.screen = pygame.display.set_mode((1200,800), pygame.RESIZABLE)
        pygame.display.set_caption('Geometry Dash')

        #timing
        self.clock = pygame.time.Clock()
        self.max_fps = 60 #tick rate
        self.dt = 0

        #making of the player
        self.player = pygame.Rect(100, 0, 50, 50) # x, y, w, h ---> this is the hitbox
        self.player_imgs = utilies.SpriteSheet()
        self.player_imgs.extract_single_image("player_sprites/Simple_cube.jpg", self.player.size, 255)
        self.rotation = 0
        self.GRAVITY = -9.8 # all caps = constant
        self.velocity = pygame.Vector2(0, 0)
        self.mass = 3
        self.jump = False
        self.mode = "Cube"

        #making of ground
        self.ground = pygame.Rect(0, 480, 1200, 800)


        #Editor
        self.world = Editor(1, False, self.ground.y) #KIAN IT DOESNT WORK, only W and A keys work and super glichy and slow, I am disabling it for now
        self.debug = True

    
    def run(self):
        while True:
            self.screen.fill((116,75,196)) #rgb - 255-0
            self.dt = self.clock.tick(60)/1000 # the number inside is the fps or will also tick rate
 
            #update physics or level editor
            if not self.world.editor:
                self.apply_player_physics()
            else:
                self.world.level_editor()
            self.world.update_world(5)
            #event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_SPACE and self.jump:
                        self.velocity.y = -15
                        self.jump = False


                if event.type == pygame.MOUSEBUTTONDOWN and self.jump:

                        self.velocity.y = -15
                        self.jump = False
            
            #draw stuff
            self.draw()

            pygame.display.update()
            if self.debug:
                print(self)
                print(self.world)
                print(f"Vel: {self.velocity} \nDt: {self.dt} \nCan Jump: {self.jump} \nOS: {os.name}")
                os.system('cls' if os.name == 'nt' else 'clear')

    def draw(self):
        if self.world.editor:
            self.world.draw_grid()

        #draw player
        #add rotation to player
        if not self.jump:
            self.rotation = (self.rotation - 600 * self.dt) % 360
        self.player_imgs.images[0] = pygame.transform.rotate(
            self.player_imgs.original_image[0],
            self.rotation
        ).convert_alpha()
        
        self.screen.blit(self.player_imgs.get_image(0).convert_alpha(), self.player) #type: ignore
        if self.debug: pygame.draw.rect(self.screen, (255,0,0), self.player, 2)
            
        pygame.draw.rect(self.screen, (0,225,0), self.ground)
        
       
    def apply_player_physics(self):

        #update player first
        self.player.move_ip(self.velocity)

        #gravity
        self.velocity.y -= self.GRAVITY * self.mass * self.dt
        self.velocity.y = min(self.velocity.y, 50)

        #ground colliton
        if self.player.colliderect(self.ground) : # rect vs rect: if collide => True no collide => False
            self.jump = True
            self.rotation = 0
            self.velocity.y = 0
            self.player.y = (self.ground.y - self.player.h)

    






if __name__ == '__main__':
    app = Geometry_dash()
    app.run()




