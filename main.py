from email import utils
import os
import sys
import pygame  # main lib for rendering
import numpy as np
import player as p
from ui import Card
from world import *
import music
import utility
import math

"""
var = utility.load_sound("Music/file")
"""

class Geometry_dash:

    def __init__(self, map_name="Trial.json"):
        # center the window
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        # screen init
        pygame.init()
        pygame.display.init()
        pygame.mixer.init()
        self.FULL_SCREEN_SIZE = utility.get_fullscreen()
        self.last_screen_size = utility.BASE_SIZE
        self.window = pygame.display.set_mode(utility.BASE_SIZE, pygame.RESIZABLE)
        self.scale = {"width": 1, "height": 1, "overall": 1}
        self.display = pygame.Surface(utility.BASE_SIZE)
        pygame.display.set_caption('Geometry Dash')

        # timing
        self.clock = pygame.time.Clock()
        self.max_fps = 120  # tick rate
        self.dt = 0

        # UI STUFF
        self.deaths = 0
        self.percentage = 0

        # background
        self.ground = pygame.Rect(0, 480, 1200, 800)
        self.bg = utility.SpriteSheet()
        self.bg.extract_single_image("Textures/bg.jpg", (utility.BASE_SIZE[0], utility.BASE_SIZE[1]), 255)
        self.bg_scroll = 0
        self.bg_scroll_2 = utility.BASE_SIZE[0]
        self.bg_hue = 0
        self.speed = 700
        self.tint_surface = pygame.Surface(utility.BASE_SIZE, pygame.SRCALPHA)

        # SFX Setup
        self.sfx = music.Music(1)

        # Editor 
        self.world = Editor(
            [[3,0,0,0],[5, 0, 0, 4]], True, self.ground.y, self.display
        )
        self.world.reset()

        self.world.load_from_dict(utility.load_map(map_name))

        self.world.reset()

        self.p = p.Player(self.world) # player

        self.debug = True  # for hitbox
        self.Text_debug = False  # for console logs

        #get settings
        self.settings = utility.load_map("settings.json", settings=True)

    # -------------------- MAIN LOOP --------------------

    def run(self):
        while True:
            #os.system('cls' if os.name == 'nt' else 'clear')
            # Calculate scaling
            window_w, window_h = self.window.get_size()
            base_h = utility.BASE_SIZE[1]

            if window_h == 0: window_h = 1
            scale = window_h / base_h # Calculate the scale factor based on height, since we want to maintain aspect ratio. We use the base height as the reference for scaling.
            logical_w = int(window_w / scale)
            logical_h = base_h

            if self.display.get_width() != logical_w or self.display.get_height() != logical_h:
                if (
                self.display.get_width(), self.display.get_height()) != self.FULL_SCREEN_SIZE: self.last_screen_size = (
                self.display.get_width(), self.display.get_height())
                self.bg.rezize_images((logical_w, logical_h))
                self.display = pygame.Surface((logical_w, logical_h))
                self.tint_surface = pygame.Surface((logical_w, logical_h), pygame.SRCALPHA)
                self.ground.width = logical_w
                self.world.screen = self.display

            # Mouse correction
            mx, my = pygame.mouse.get_pos()
            mouse_pos = (mx / scale, my / scale)

            self.display.fill((116, 75, 196))  # rgb - 255-0
            self.dt = self.clock.tick(self.max_fps) / 1000  # the number inside is the fps or will also tick rate
            # draw stuff
            self.draw(mouse_pos)
            # update physics or level editor
            if not self.world.editor:
                d = self.p.apply_physics(self.world, self.ground, self.debug, self.dt)
                if not d: self.death()
            else:
                move_type = self.world.level_editor(mouse_pos) #move_type[x][0] = bool (move in that direction?) : move_type[x][1] = int (velocity)
                if move_type[0][0]: self.p.player.move_ip(0, move_type[0][1]);self.ground.move_ip(0, move_type[0][1])  # up
                if move_type[1][0]: self.p.player.move_ip(0, move_type[1][1]);self.ground.move_ip(0, move_type[1][1])  # down
                if move_type[2][0]: self.p.player.move_ip(move_type[2][1], 0)  # left
                if move_type[3][0]: self.p.player.move_ip(move_type[3][1], 0)  # right

            collide = self.world.update_world(
                self.world.grid * 10 * self.dt, self.p.player,
                self.debug)

            if collide and not self.debug:
                self.death()

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                self.world.change_place_type(event)  # update the block type to be placed in the editor

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_F3:
                        self.debug = not self.debug
                    if event.key == pygame.K_F4:
                        self.Text_debug = not self.Text_debug
                    if event.key == pygame.K_F5 and self.world.editor:
                        self.simulate = not self.simulate
                    if event.key == pygame.K_F2:
                        self.world.editor = not self.world.editor
                        if self.world.objects["PlayerSpawn"] is None: self.world.objects["PlayerSpawn"] = self.world.objects["Start"]  # If no spawn point is set, the start point will be the spawn point
                        self.world.reset()  # Reset camera scroll when toggling editor mode
                        start_point = self.world.get_start_point()
                        self.p.player.x = start_point.x - self.world.x_scroll
                        self.p.player.y = start_point.y + (start_point.height - self.p.player.height)
                        self.ground.topleft = (0, 480)  # Reset ground position when toggling editor mode
                        self.sfx.music_controls(obj=self.world.objects, scroll=self.world.x_scroll)
                    if event.key == pygame.K_r and (event.mod & pygame.KMOD_CTRL):
                        self.world.set_level([[3,0,0,0],[5, 0, 0, 4]])
                        start_point = self.world.get_start_point()
                        self.p.player.x = start_point.x - self.world.x_scroll
                        self.p.player.y = start_point.y + (start_point.height - self.p.player.height)
                        self.ground.topleft = (0, 480)  # Reset ground position when toggling editor mode

                    if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                        data = self.world.__dict__()
                        utility.save_map("Stereo Madness.json", data)

                    if event.key == pygame.K_p and self.world.editor:
                        self.sfx.music_controls(obj=self.world.objects, scroll=self.world.x_scroll)

                    if event.key == pygame.K_F11:
                        if utility.get_fullscreen() == self.FULL_SCREEN_SIZE:
                            self.screen = pygame.display.set_mode(utility.BASE_SIZE, pygame.RESIZABLE)
                        else:
                            self.screen = pygame.display.set_mode(self.FULL_SCREEN_SIZE)

                if event.type == pygame.VIDEORESIZE:  # Updated to VIDEORESIZE for modern pygame
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Render to window
            scaled_display = pygame.transform.scale(self.display, (window_w, window_h))
            self.window.blit(scaled_display, (0, 0))

            pygame.display.update()
            if self.Text_debug:
                os.system('cls' if os.name == 'nt' else 'clear')
                #print(self)
                #print(self.world)
                #print(collide)
                print(self.dt)

    # -------------------- MAIN Menu --------------------
    def main_menu(self):
        # --- Initialize UI Elements ---
        # Calculate a centered position for the button using logical BASE_SIZE
        btn_w, btn_h = 200, 200 
        center_x = utility.BASE_SIZE[0] / 2 - (btn_w / 2)
        center_y = utility.BASE_SIZE[1] / 2 - (btn_h / 2)
        
        play_rect = pygame.Rect(center_x, center_y, btn_w, btn_h)
        play_btn = utility.button("Buttons/play.png", play_rect)

        while True:
            # Calculate scaling
            window_w, window_h = self.window.get_size()
            base_h = utility.BASE_SIZE[1]

            if window_h == 0: window_h = 1
            scale = window_h / base_h # Calculate the scale factor based on height
            logical_w = int(window_w / scale)
            logical_h = base_h

            if self.display.get_width() != logical_w or self.display.get_height() != logical_h:
                if (self.display.get_width(), self.display.get_height()) != self.FULL_SCREEN_SIZE: 
                    self.last_screen_size = (self.display.get_width(), self.display.get_height())
                self.bg.rezize_images((logical_w, logical_h))
                self.display = pygame.Surface((logical_w, logical_h))
                self.tint_surface = pygame.Surface((logical_w, logical_h), pygame.SRCALPHA)
                self.ground.width = logical_w
                self.world.screen = self.display

            # Mouse correction (Passes logical coordinates to the button)
            mx, my = pygame.mouse.get_pos()
            mouse_pos = (mx / scale, my / scale)

            self.dt = self.clock.tick(self.max_fps) / 1000
            self.display.fill((0, 0, 0))
            
            # draw the bg
            self.draw(mouse_pos, True)

            # actual loop
            utility.render_text("Geometry Dash", (utility.get_fullscreen()[0] / 2, 50), round(50*scale), color="White", surface=self.display, center=True)
            
            # --- Draw and Update Button ---
            os.system("cls" if os.name == "nt" else "clear")  # Clear console for debugging
            play_btn.draw(self.display, True)
            if play_btn.update(mouse_pos):
                    if pygame.mouse.get_pressed()[0]:
                        self.levels_menu()  # Go to levels menu on click 
                        #self.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_F11:
                        if utility.get_fullscreen() == self.FULL_SCREEN_SIZE:
                            pygame.display.set_mode(utility.BASE_SIZE, pygame.RESIZABLE)
                        else:
                            pygame.display.set_mode(self.FULL_SCREEN_SIZE)

                if event.type == pygame.VIDEORESIZE:  # Updated to VIDEORESIZE for modern pygame
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Render to window
            scaled_display = pygame.transform.scale(self.display, (window_w, window_h))
            self.window.blit(scaled_display, (0, 0))
            self.scale_window(window_w, window_h, **{"class": play_btn})
            pygame.display.update()

    def levels_menu(self):
        # --- Initialize UI Elements ---
        # Calculate a centered position for the button using logical BASE_SIZE

        #get all the levels
        all_levels = self.settings["levels"]        
        # Wait for the mouse button to be released before allowing interaction to prevent instant triggers
        wait_for_release = pygame.mouse.get_pressed()[0]
        
        
        cards = [Card(all_levels[i], pygame.Rect(utility.BASE_SIZE[0] / 2 - 100, 150 + i*250, 200, 200)) for i, level in enumerate(all_levels)]

        while True:
            # Calculate scaling
            window_w, window_h = self.window.get_size()
            base_h = utility.BASE_SIZE[1]

            if window_h == 0: window_h = 1
            scale = window_h / base_h # Calculate the scale factor based on height
            logical_w = int(window_w / scale)
            logical_h = base_h

            if self.display.get_width() != logical_w or self.display.get_height() != logical_h:
                if (self.display.get_width(), self.display.get_height()) != self.FULL_SCREEN_SIZE: 
                    self.last_screen_size = (self.display.get_width(), self.display.get_height())
                self.bg.rezize_images((logical_w, logical_h))
                self.display = pygame.Surface((logical_w, logical_h))
                self.tint_surface = pygame.Surface((logical_w, logical_h), pygame.SRCALPHA)
                self.ground.width = logical_w
                self.world.screen = self.display

            # Mouse correction (Passes logical coordinates to the button)
            mx, my = pygame.mouse.get_pos()
            mouse_pos = (mx / scale, my / scale)

            self.dt = self.clock.tick(self.max_fps) / 1000
            self.display.fill((0, 0, 0))
            
            # draw the bg
            self.draw(mouse_pos, True)

            # actual loop
            utility.render_text("Select LEVEL", (utility.get_fullscreen()[0] / 2, 50), round(50*scale), color="White", surface=self.display, center=True)
            
            # --- Draw and Update Button ---
            os.system("cls" if os.name == "nt" else "clear")  # Clear console for debugging
        
            for card in cards:
                card.draw(self.display)
                if card.update(mouse_pos):
                    self.world.load_from_dict(utility.load_map(f"{card.level_name}.json"))
                    self.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_F11:
                        if utility.get_fullscreen() == self.FULL_SCREEN_SIZE:
                            self.screen = pygame.display.set_mode(utility.BASE_SIZE, pygame.RESIZABLE)
                        else:
                            self.screen = pygame.display.set_mode(self.FULL_SCREEN_SIZE)
                      

                if event.type == pygame.VIDEORESIZE:  # Updated to VIDEORESIZE for modern pygame
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            # Render to window
            scaled_display = pygame.transform.scale(self.display, (window_w, window_h))
            self.window.blit(scaled_display, (0, 0))
            self.scale_window(window_w, window_h, **{"class": cards})
            pygame.display.update()


    def draw(self, mouse_pos, main_menu = False):
        #Debug
        """
        if self.rotation > self.rotation_to:
            rot_color = (255, 0, 0)
        elif self.rotation == self.rotation_to:
            rot_color = (255, 255, 255)
        else:
            rot_color = (0, 255, 0)
        """

        # DRAW ORDER:
        # 1. Background (already filled with color)
        # 2. World (blocks and spikes)
        # 3. Ground (drawn before player so player can go behind it)
        # 4. Player (drawn after ground so it can go behind it)
        # 5. Music playback (only shows if level editor is enabled and music is playing)

        # Update background tint

        color = pygame.Color(255, 255, 255)
        if not self.world.editor or main_menu:
            color = pygame.Color(255, 255, 255)
            self.bg_hue = (self.bg_hue + 10 * self.dt) % 360
            color = pygame.Color(0)
            color.hsva = (self.bg_hue, 70, 100, 100)

        bg_img = self.bg.get_image(0)
        # draw background
        self.display.blit(bg_img, (self.bg_scroll, 0))
        self.display.blit(bg_img, (self.bg_scroll_2, 0))
        if main_menu or not self.world.editor:
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
        if main_menu: return
        pygame.draw.rect(self.display, "dark green", self.ground)

        if not self.world.editor: utility.render_text(f"DEATHS: {self.deaths}", (
            -((self.world.x_scroll)+500) + utility.get_fullscreen()[0] / 3, utility.get_fullscreen()[1] / 2), color="Black",
                                surface=self.display)

        # draw player
        self.display.blit(self.p.player_imgs.get_image(0), self.p.Player_rect if not self.world.editor else self.p.player)

        # draw music related stuff if music is playing and editor is enabled
        if self.world.editor: self.sfx.draw(self.display, self.world.grid * 10 * self.dt, self.world.x_scroll)

        # draw UI and debug info
        if self.debug and False:
            pos = pygame.Vector2(mouse_pos) + pygame.Vector2(self.world.x_scroll, self.world.y_scroll)
            utility.render_text(f"FPS: {round(self.clock.get_fps())}", (10, 10), 20, surface=self.display)
            utility.render_text(f"Player: {self.player}", (10, 30), 20, surface=self.display)
            utility.render_text(f"Mouse: {pos}", (10, 70), 20, surface=self.display)
            utility.render_text(
                f"Mouse Grid: ({(pos.x // self.world.grid) * self.world.grid}, {(pos.y // self.world.grid) * self.world.grid})",
                (10, 90), 20, surface=self.display)
            utility.render_text(f"Image Size: {self.player_imgs.get_image(0).get_size()}", (10, 50), 20,
                                surface=self.display)
            utility.render_text(f"Rotation: {round(self.rotation, 3)}", (10, 110), 20, rot_color, surface=self.display)
            utility.render_text(f"Rotation: {round(self.rotation, 3)}", (10, 110), 20, rot_color, surface=self.display) # pyright: ignore[reportArgumentType]
            utility.render_text(f"Rotation_To: {self.rotation_to}", (10, 130), 20, surface=self.display)
            utility.render_text(f"Rotation_Velocity: {round(self.rotation_velocity, 3)}", (10, 150), 20, surface=self.display)
            utility.render_text(f"World Scroll {self.world.x_scroll, self.world.y_scroll}", (10, 170), 20,
                                surface=self.display)
            utility.render_text(
                f"Death pos {(-((self.world.x_scroll / 10) + 384) + utility.get_fullscreen()[0] / 3, utility.get_fullscreen()[1] / 2)}",
                (10, 210), 20, surface=self.display)

            utility.render_text(
                f"Level Length {self.world.level_dist} and Level completion {self.world.level_completion}",
                (10, 260), 20, surface=self.display)
            utility.render_text(
                f"Velocity.Y: {round(self.velocity.y)}", (10, 280), 20, surface=self.display
            )

            pygame.draw.rect(self.display, (255, 0, 0), self.player, 2)
            if not self.world.editor: pygame.draw.rect(self.display, (255, 0, 255), self.Player_rect, 2)
            
    def scale_window(self, w, h, **kwargs): 
        self.scale = {
        "width": self.window.get_width() / utility.BASE_SIZE[0], 
        "height": self.window.get_height() / utility.BASE_SIZE[1],
        "overall": min(self.window.get_width() / utility.BASE_SIZE[0], self.window.get_height() / utility.BASE_SIZE[1])
        }

        for key, value in kwargs.items(): 
            if key == "class":
                if type(value) == list:
                    for obj in value:
                        if hasattr(obj, "resize"):
                            obj.resize(self.scale)
                        else:
                            raise Exception(f"Object of type {type(obj)} does not have a resize method")
                else:
                    if hasattr(value, "resize"):
                        value.resize(self.scale)
                    else:
                        raise Exception(f"Object of type {type(value)} does not have a resize method")

        if self.display.get_size() != self.FULL_SCREEN_SIZE: 
            self.last_screen_size = (w, h)

    def death(self):
        self.world.reset()
        start_point = self.world.get_start_point()
        self.p.player.x = start_point.x - self.world.x_scroll
        self.p.player.y = start_point.y + (start_point.height - self.p.player.height)
        self.p.velocity.y = 0
        self.rotation = 0  # If collided with a cube kill_zone, exit the game
        self.deaths += 1

    def __str__(self):
        return f"""
        Vel: {self.p.velocity}
        Dt: {self.dt}
        Can Jump: {self.p.jump}
        OS: {os.name}
        Cube Rotation: {math.sin(self.rotation):.3f}
        """


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')  # reset console on start
    app = Geometry_dash(map_name="Stereo Madness.json")
    app.main_menu()