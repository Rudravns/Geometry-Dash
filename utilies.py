import os
from numpy import save
import pygame
from typing import *  # pyright: ignore[reportWildcardImportFromLibrary]

import json


pygame.init()
pygame.display.init()
pygame.font.init()





# ====================================================
# Screen Funcs
# ====================================================
BASE_SIZE = (1200,800)
def get_fullscreen():
    return pygame.display.Info().current_w, pygame.display.Info().current_h

    
@overload
def scale(value: int | float, *, round_values: bool = False) -> int | float: ...


@overload
def scale(
        value: tuple[int | float, ...],
        *,
        round_values: bool = False
) -> tuple[int | float, ...]: ...


def scale(
        value: int | float | tuple[int | float, ...],
        *,
        round_values: bool = False
) -> int | float | tuple[int | float, ...]:
    """Scale a value or tuple of values based on the current fullscreen resolution."""
    screen_w, screen_h = get_fullscreen()
    base_w, base_h = BASE_SIZE  # Base resolution for scaling

    scale_factor = min(screen_w / base_w, screen_h / base_h)

    if isinstance(value, (int, float)):
        scaled_value = value * scale_factor
        return round(scaled_value) if round_values else scaled_value

    if isinstance(value, tuple):
        return tuple(scale(v, round_values=round_values) for v in value)

    raise TypeError("Value must be an int, float, or tuple of int/float.")


# =====================================================
# Text rendering
# =====================================================
def render_text(
        text: str,
        position,
        size: int = 50,
        color = "#000000",
        font: Optional[pygame.font.Font] = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        draw: bool = True
) -> Tuple[pygame.Surface, pygame.Rect]:
    """Render text to the active display surface."""

    screen = pygame.display.get_surface()
    if screen is None:
        raise RuntimeError("Display surface not initialized. Call pygame.display.set_mode().")

    # Create font if none provided
    if font is None:
        font = pygame.font.SysFont("Arial", size)

    # Convert color string to pygame.Color
    if isinstance(color, str):
        color = pygame.Color(color)  # type: ignore

    # Apply font styles
    font.set_bold(bold)
    font.set_italic(italic)
    font.set_underline(underline)

    # Render text
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect(topleft=position)

    if draw:
        screen.blit(text_surface, text_rect)

    return text_surface, text_rect


# =====================================================
# Loading / Saving Files
# =====================================================
def load_image(path: str) -> pygame.Surface:
    """Load an image from disk with alpha support."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.abspath(
            os.path.join(script_dir, "asset")
        )
        image = pygame.image.load(os.path.join(BASE_DIR, path))
        return image
    except pygame.error as e:
        raise FileNotFoundError(f"Unable to load image at '{path}': {e}") from e


def load_font(path: str, size: int) -> pygame.font.Font:
    """Load a font from disk."""
    try:
        return pygame.font.Font(path, size)
    except IOError as e:
        raise FileNotFoundError(f"Unable to load font at '{path}': {e}") from e


def load_sound(path: str) -> pygame.mixer.Sound:
    """Load a sound from disk."""
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        raise FileNotFoundError(f"Unable to load sound at '{path}': {e}") from e


# =====================================================
# Sprite Sheets
# =====================================================
class SpriteSheet:
    def __init__(self):
        #only init
        self.sprite_sheet: pygame.Surface = None
        self.sprite_sheet_rect: pygame.Rect = None
        self.images: List[pygame.Surface] = []
        self.original_image: List[pygame.Surface] = []
        
    # ---------------------------------------------------------
    # Method 1: Extract using a list of Rects
    # ---------------------------------------------------------
    def extract_from_rects(
        self,
        path: str,
        rects: List[pygame.Rect],
        scale: Tuple[int, int],
        alpha: int = 255
    ) -> List[pygame.Surface]:
        self.sprite_sheet = load_image(path)
        self.sprite_sheet_rect = self.sprite_sheet.get_rect()
        images: List[pygame.Surface] = []

        for rect in rects:
            image = pygame.Surface(rect.size, pygame.SRCALPHA)
            image.blit(self.sprite_sheet, (0, 0), rect)
            image = pygame.transform.scale(image, scale)
            image.set_alpha(alpha)
            images.append(image)

        self.images.extend(images)
        self.original_image.extend(images)


    # ---------------------------------------------------------
    # Method 2: Extract grid-style
    # ---------------------------------------------------------
    def extract_grid(
        self,
        path: str,
        crop_size: Tuple[int, int],
        start: Tuple[int, int] = (0, 0),
        scale: Tuple[int, int] | None = None,
        alpha: int = 255
    ) -> List[pygame.Surface]:

        self.sprite_sheet = load_image(path)
        self.sprite_sheet_rect = self.sprite_sheet.get_rect()
        images: List[pygame.Surface] = []
        
        w_crop, h_crop = crop_size
        x_start, y_start = start

        for y in range(y_start, self.sprite_sheet_rect.height, h_crop):
            for x in range(x_start, self.sprite_sheet_rect.width, w_crop):
                rect = pygame.Rect(x, y, w_crop, h_crop)

                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sprite_sheet, (0, 0), rect)

                if scale:
                    image = pygame.transform.scale(image, scale)

                image.set_alpha(alpha)
                images.append(image)
                self.original_image.append(image)

        self.images.extend(images)

    def extract_single_image(self, path: str, scale: Tuple[int, int], alpha: int = 255):
        image = load_image(path)
        image = pygame.transform.scale(image, scale)
        image.set_alpha(alpha)
        self.images.append(image)
        self.original_image.append(image)

    @overload
    def rotate_images(self, angle: int) -> None: ...

    @overload 
    def rotate_images(self, angle: int, index: int) -> None: ...

    def rotate_images(self, angle: int, index: int | None = None) -> None:
        if index is not None:
            self.images[index] = pygame.transform.rotate(self.images[index], angle)
            return
        else:
            for i in range(len(self.images)):
                self.images[i] = pygame.transform.rotate(self.images[i], angle)
            return
        
    # ---------------------------------------------------------
    def get_image(self, index: int) -> pygame.Surface:
        return self.images[index]