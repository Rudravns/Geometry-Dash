import pygame
import math
import Base_worlds


class Editor:

    def __init__(self, level, editor, ground_y):
        self.level = level  #Int
        self.screen = pygame.display.get_surface()
        
        #Editor
        self.editor = editor  #Bool
        self.editor_window = True
        self.offsetx = 0
        self.offsety = 0

        #Editor Values
        self.block = "01"  #This is temporary until further progress is made in the editor
        self.color = (0, 0, 0)
        self.color_alpha = 255
        self.outline = (255, 255, 255)
        self.outline_alpha = 255
        self.speed = 5
        self.grid = 40
        self.gridx = self.grid - self.screen.get_width() % self.grid
        self.gridy = self.grid - self.screen.get_height() % self.grid
    
        self.size_multiplier = 1

        #world attr
        self.level = Base_worlds.test
        self.ground_y = ground_y-self.grid
        self.x = self.screen.get_size()[0]

        #world objects
        self.spike = []
        self.blocks = []
        self.get_world()

    
    def level_editor(self):
        if self.editor:
            mouse = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()

            #Basic Editor Shortcuts
            if keys[pygame.K_p]:
                self.editor_window = not self.editor_window  #Opens/Closes editor window
            if keys[pygame.K_PLUS]:
                if self.grid < 100: self.grid += 20
            elif keys[pygame.K_MINUS]:
                if self.grid > 20: self.grid -= 20
            if keys[pygame.K_UP]:
                if self.size_multiplier < 3: self.size_multiplier += 0.1
            elif keys[pygame.K_DOWN]:
                if self.size_multiplier > 0.1: self.size_multiplier -= 0.1
            if keys[pygame.K_LEFT]:
                if len(self.block) > 2: self.block = self.block[1:]
            elif keys[pygame.K_RIGHT]:
                if len(self.block) < 3: self.block = "0" + self.block
            if keys[pygame.K_e]:
                return ("Add", mouse)
            elif keys[pygame.K_q]:
                return ("Delete", mouse)

            #Editor Movement
            if keys[pygame.K_w]:
                if self.offsety < 300: self.offsety -= 5
            if keys[pygame.K_s]:
                if self.offsety > 0: self.offsety += 5
            if keys[pygame.K_a]:
                if self.offsetx < 300: self.offsetx -= 5
            if keys[pygame.K_d]:
                if self.offsetx > 0: self.offsetx += 5

    def draw_grid(self):
        screen = self.screen
        linewidth = int(math.ceil(self.grid / 20))

        for x in range(int(screen.get_width() / self.gridx)):
            xl = x * self.gridx + (self.offsetx % self.grid)
            yl = screen.get_height()

            if xl + self.offsetx == screen.get_width() / 2:
                color = (0, 255, 0)
                font = pygame.font.SysFont("Arial", 20)
                text = font.render("Y", True, color)
                screen.blit(text, (xl, 20))
                screen.blit(text, (xl, yl - 20))
            else:
                color = (0, 0, 255)

            pygame.draw.line(screen, color, (xl, 0), (xl, yl), linewidth)

        for y in range(int(screen.get_height() / self.gridy)):
            yl = y * self.gridy + (self.offsety % self.grid)
            xl = screen.get_width()

            if yl + self.offsety == screen.get_height() / 2:
                color = (255, 0, 0)
                font = pygame.font.SysFont("Arial", 20)
                text = font.render("X", True, color)
                screen.blit(text, (20, yl))
                screen.blit(text, (xl - 20, yl))
            else:
                color = (0, 0, 255)

            pygame.draw.line(screen, color, (0, yl), (xl, yl), linewidth)

    def get_world(self):
        for y, row in enumerate(self.level):
            for x, block in enumerate(row):
                match block:
                    case 1:
                        # (5 - y) because the list has 6 rows (0 to 5)
                        # Row 5 in the list should be just above ground
                        self.spike.append(Spike((x * self.grid)+self.x, self.ground_y - ((5 - y) * self.grid), self.grid))
                    case 2:
                        self.blocks.append(pygame.Rect(x* self.grid+self.x, self.ground_y - ((5 - y) * self.grid), self.grid, self.grid))
                    case _:
                        continue
    def update_world(self, speed, player_hitbox):
        # self.x -= speed # Removed this as it was causing confusion with individual object positions
        for spike in self.spike:
            spike.move(-speed, 0)
            spike.draw(self.screen)
            
            
        for block in self.blocks:
            block.move_ip(-speed, 0)
            pygame.draw.rect(self.screen, (255, 255, 255), block)

        for spike in self.spike:
            if spike.check_collition(player_hitbox):
                return True
        for block in self.blocks:
            if block.colliderect(player_hitbox):
                return True
        return False    
       
        
    def __str__(self):
        return f"Block: {self.block}"

class Spike:

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

        self.vert = [
            [self.x + self.size // 2, self.y],
            [self.x, self.y + self.size],
            [self.x + self.size, self.y + self.size],
        ]

    def move(self, x, y):
        self.x += x
        self.y += y

        self.vert = [
            [self.x + self.size // 2, self.y],
            [self.x, self.y + self.size],
            [self.x + self.size, self.y + self.size],
        ]
        
    def draw(self, screen):
        pygame.draw.polygon(screen, (255, 255, 255), self.vert)

    def check_collition(self, hitbox: pygame.Rect) -> bool:
        # 1. Quick check: is the player even near the spike's bounding area?
        spike_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        if not hitbox.colliderect(spike_rect):
            return False

        # 2. Precise check: do any of the triangle's 3 sides cross the player rect?
        # We check lines: (0->1), (1->2), and (2->0)
        lines = [
            (self.vert[0], self.vert[1]),
            (self.vert[1], self.vert[2]),
            (self.vert[2], self.vert[0])
        ]

        for start, end in lines:
            if hitbox.clipline(start, end):
                return True

        # 3. Final check: is the player completely inside the triangle?
        # (Usually covered by clipline, but good for very small players)
        return hitbox.collidepoint(self.vert[0])
