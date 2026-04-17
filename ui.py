import pygame
import utility

class Card:
    def __init__(self, level_name, rect):
        self.level_name = level_name
        self.rect = rect
        self.org_rect = rect.copy()
        self.out_color = "#1f07b8"
        self.in_color = "#5a41fa"
        self.clicked = False

    def draw(self, screen):
        # Draw the card background and border
        pygame.draw.rect(screen, self.in_color, self.rect)
        pygame.draw.rect(screen, self.out_color, self.rect, 6)
        # Render the level name text centered within the card
        utility.render_text(self.level_name, self.rect.center, size=30, color="White", surface=screen, center=True)

    def update(self, mouse_pos):
        action = False
        
        # Handle hover effect (inflation) and click detection
        if self.rect.collidepoint(mouse_pos):
            self.rect = self.org_rect.inflate(10, 10)
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        else:
            self.rect = self.org_rect
            
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
            
        return action

    def resize(self, scale: dict):
        """Scale the card based on the provided scale dictionary."""
        self.rect.width = self.org_rect.width * scale["overall"]
        self.rect.height = self.org_rect.height * scale["overall"]
        self.rect.x = self.org_rect.x * scale["width"]
        self.rect.y = self.org_rect.y * scale["height"]
        
        # Update org_rect is not needed here as it serves as the coordinate baseline