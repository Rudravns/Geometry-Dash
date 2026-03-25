from matplotlib.pylab import MT19937
import pygame
import math
import utility

class Editor:

    def __init__(self, level, editor, ground_y, surface):
        self.screen = surface
        self.movement_timer = utility.Timer(0.1)
        self.movement_timer.start()

        # Editor state
        self.editor = editor
        self.editor_window = True
        self.place_type = 1  # 1 for spike, 2 for block, 3 for start, 4 for end
        self.place_type_refrence = {
            1 : "Spike",
            2 : "Block",
            3 : "Start",
            4 : "End",
            5 : "Player Spawn"
        }

        # Grid
        self.grid = 40
        self.grid_color = (70, 70, 70)
        self.origin_color = (255, 60, 60)
        self.origin_thickness = 4

        # Camera (origin centered)
        width, height = self.screen.get_size()
        self.x_scroll = -width // 2
        self.y_scroll = 0
        self.level_completion = 0
        self.level_dist = 0
        self.m3_mousepos = (0, 0) # For scrolling through the editor
        self.SCROLL_SENSE = 4 #Constant for how fast the camera scrolls with the mouse

        # World
        self.level = level
        self.world_origin_y = ground_y
        self.block_start = self.get_start_block()#the world grid pos for the first bloc (the starting point)

        # World objects (WORLD COORDS)
        self.objects = {
            "Spike": [],
            "Block": [],
            "Start": pygame.Rect(0, 440, self.grid, self.grid),
            "End": pygame.Rect(4240, 440, self.grid, self.grid),
            "PlayerSpawn": None
        }

        #init textures
        #
        # assets HAS to be 16x16 tex size
        #

        #cube tex
        self.cube_tex = utility.SpriteSheet()
        self.cube_tex.extract_grid(path="Textures/Cube.png", crop_size=(16,16), scale=(self.grid, self.grid), alpha=255)
        self.cube_animation_timer = utility.Timer(0.1)
        self.cube_animation_timer.start()
        self.cube_img = 0

        #flag tex
        self.flag_tex = utility.SpriteSheet()
        self.flag_tex.extract_grid(path="Textures/flag.png", crop_size=(16,16),  scale=(self.grid, self.grid), alpha=255)
        self.flag_animation_timer = utility.Timer(0.3)
        self.flag_animation_timer.start()
        self.flag_img = 0

        # spike tex
        self.spike_tex = utility.SpriteSheet()
        self.spike_tex.extract_grid(path="Textures/Spike.png", crop_size=(16, 16), scale=(self.grid, self.grid),alpha=255)
        self.spike_animation_timer = utility.Timer(0.04)
        self.spike_animation_timer.start()
        self.spike_img = 0

        #missing tex
        self.miss_tex = utility.SpriteSheet()
        self.miss_tex.extract_grid(path="Textures/missing.png", crop_size=(16, 16), scale=(self.grid, self.grid), alpha=255)




        self.get_world()

    # ===============================
    # EDITOR UPDATE
    # ===============================
    def level_editor(self, mouse_pos):
        keys = pygame.key.get_pressed()
        movement_type = [[0, 0], [0, 0], [0, 0], [0, 0]] #move_type[x][0] = bool (move in that direction?) : move_type[x][1] = int (velocity)

        if self.movement_timer.has_elapsed():

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x_scroll -= self.grid
                movement_type[2] = [1, self.grid]

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x_scroll += self.grid
                movement_type[3] = [1, -self.grid]

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y_scroll -= self.grid
                movement_type[0] = [1, self.grid]

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y_scroll += self.grid
                movement_type[1] = [1, -self.grid]


            self.movement_timer.reset()
            self.movement_timer.start()

        # draw the grid and objects
        self.draw_grid_objects()
        mouse_pos = self.draw_grid(mouse_pos)
        mouse_down = pygame.mouse.get_pressed()
        world_mos_pos = pygame.Vector2(mouse_pos) + pygame.Vector2(self.x_scroll, self.y_scroll)
        world_grid_mos_pos = (math.floor(world_mos_pos.x // self.grid) * self.grid, math.floor(world_mos_pos.y // self.grid) * self.grid)

        # Vars for mouse scrolling
        prev_x_scroll = self.x_scroll
        prev_y_scroll = self.y_scroll
        cont = True
        for i in movement_type:
            if i[0] == 1:
                cont = False
                break

        if mouse_down[0] and world_grid_mos_pos[1] < self.world_origin_y:  # left click to place and is above the ground
            world_x = mouse_pos[0] + self.x_scroll
            world_y = mouse_pos[1] + self.y_scroll
            grid_x = (world_x // self.grid) * self.grid
            grid_y = (world_y // self.grid) * self.grid

            new_rect = pygame.Rect(grid_x, grid_y, self.grid, self.grid)

            match self.place_type:
                case 1:  # Spike
                    # Prevent overlap with any block, spike, start, or end
                    if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                    and not new_rect.colliderect(self.objects["Start"]) \
                    and not new_rect.colliderect(self.objects["End"]) \
                    and not any(block.colliderect(new_rect) for block in self.objects["Block"]):

                        sides = ["Pointing Up", "Pointing Right", "Pointing Down", "Pointing Left"]
                        indices_to_check = []
                        for i in range(4):
                            if keys[pygame.K_1 + i]:
                                indices_to_check.append(i)
                        
                        if not indices_to_check:
                            indices_to_check = [0, 1, 2, 3]

                        for i in indices_to_check:
                            side = sides[i]
                            supported = False
                            
                            if side == "Pointing Up":
                                check_rect = pygame.Rect(grid_x, grid_y + self.grid, self.grid, self.grid)
                                if (grid_y + self.grid >= self.world_origin_y) or \
                                   any(block.colliderect(check_rect) for block in self.objects["Block"]):
                                    supported = True
                            elif side == "Pointing Right":
                                check_rect = pygame.Rect(grid_x - self.grid, grid_y, self.grid, self.grid)
                                if any(block.colliderect(check_rect) for block in self.objects["Block"]):
                                    supported = True
                            elif side == "Pointing Down":
                                check_rect = pygame.Rect(grid_x, grid_y - self.grid, self.grid, self.grid)
                                if any(block.colliderect(check_rect) for block in self.objects["Block"]):
                                    supported = True
                            elif side == "Pointing Left":
                                check_rect = pygame.Rect(grid_x + self.grid, grid_y, self.grid, self.grid)
                                if any(block.colliderect(check_rect) for block in self.objects["Block"]):
                                    supported = True
                            
                            if supported:
                                self.objects["Spike"].append(Spike(grid_x, grid_y, self.grid, side=side))
                                break
                    

                case 2:  # Block
                    # Prevent overlap with spikes, start, or end
                    if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                    and not new_rect.colliderect(self.objects["Start"]) \
                    and not new_rect.colliderect(self.objects["End"]) \
                    and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                        self.objects["Block"].append(new_rect)

                case 3:  # Start
                    # Move start only if not colliding with blocks or spikes
                    if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                    and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                        self.objects["Start"].x = grid_x
                        self.objects["Start"].y = grid_y

                case 4:  # End
                    # Move end only if not colliding with blocks or spikes
                    if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                    and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                        self.objects["End"].x = grid_x
                        self.objects["End"].y = grid_y
                case 5:  # Player Spawn
                    # Prevent overlap with spikes, start, end, or blocks
                    if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                    and not new_rect.colliderect(self.objects["Start"]) \
                    and not new_rect.colliderect(self.objects["End"]) \
                    and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                        
                        # Check support (Must be on ground OR on top of a block)
                        check_rect = pygame.Rect(grid_x, grid_y + self.grid, self.grid, self.grid)
                        supported = False
                        if (grid_y + self.grid >= self.world_origin_y) or \
                           any(block.colliderect(check_rect) for block in self.objects["Block"]):
                            supported = True
                        
                        if supported:
                            self.objects["PlayerSpawn"] = new_rect
                case _:
                    raise ValueError("This block doesn't exist")
            

        elif mouse_down[2]:  # right click to remove
            world_x = mouse_pos[0] + self.x_scroll
            world_y = mouse_pos[1] + self.y_scroll
            grid_x = (world_x // self.grid) * self.grid
            grid_y = (world_y // self.grid) * self.grid
            click_rect = pygame.Rect(grid_x, grid_y, self.grid, self.grid)

            # Remove Spike
            for spike in self.objects["Spike"]:
                if spike.check_collition(click_rect, rect_to_rect=True):
                    self.objects["Spike"].remove(spike)
                    break

            # Remove Block
            for block in self.objects["Block"]:
                if block.colliderect(click_rect):
                    self.objects["Block"].remove(block)

            # Remove Player Spawn
            if self.objects["PlayerSpawn"] and self.objects["PlayerSpawn"].colliderect(click_rect):
                self.objects["PlayerSpawn"] = None

                # Check for unsupported spikes
                spikes_to_remove = []
                for spike in self.objects["Spike"]:
                    supported = False
                    if spike.type == "Pointing Up":
                        check_rect = pygame.Rect(spike.x, spike.y + self.grid, self.grid, self.grid)
                        if (spike.y + self.grid >= self.world_origin_y) or \
                            any(b.colliderect(check_rect) for b in self.objects["Block"]):
                            supported = True
                    elif spike.type == "Pointing Right":
                        check_rect = pygame.Rect(spike.x - self.grid, spike.y, self.grid, self.grid)
                        if any(b.colliderect(check_rect) for b in self.objects["Block"]):
                            supported = True
                    elif spike.type == "Pointing Down":
                        check_rect = pygame.Rect(spike.x, spike.y - self.grid, self.grid, self.grid)
                        if any(b.colliderect(check_rect) for b in self.objects["Block"]):
                            supported = True
                    elif spike.type == "Pointing Left":
                        check_rect = pygame.Rect(spike.x + self.grid, spike.y, self.grid, self.grid)
                        if any(b.colliderect(check_rect) for b in self.objects["Block"]):
                            supported = True
                    
                    if not supported:
                        spikes_to_remove.append(spike)
                
                    for s in spikes_to_remove:
                        self.objects["Spike"].remove(s)
                        break
            
        else: # middle click to move through the editor with the mouse
            if mouse_down[1] and cont:
                self.x_scroll += (mouse_pos[0] - self.m3_mousepos[0]) // (self.grid / self.SCROLL_SENSE)
                self.y_scroll += (mouse_pos[1] - self.m3_mousepos[1]) // (self.grid / self.SCROLL_SENSE)
            else:
                self.m3_mousepos = mouse_pos
            
                if self.x_scroll % self.grid - self.grid < self.grid//2: self.x_scroll -= self.x_scroll % self.grid
                else: self.x_scroll += self.grid - (self.x_scroll % self.grid)

                if self.y_scroll % self.grid - self.grid < self.grid//2: self.y_scroll -= self.y_scroll % self.grid
                else: self.y_scroll += self.grid - (self.y_scroll % self.grid)

        if cont:
            x = self.x_scroll - prev_x_scroll
            y = self.y_scroll - prev_y_scroll
            
            if x > 0: movement_type[3] = [1, -x]
            else: movement_type[2] = [1, -x]
            if y > 0: movement_type[1] = [1, -y]
            else: movement_type[0] = [1, -y]

        """
        #Old Code for mouse scrolling, ignore
        else:
            if mouse_down[1]: # middle click to move through the editor with the mouse
                self.x_scroll += (mouse_pos[0] - self.m3_mousepos[0]) // self.grid
                self.y_scroll += (mouse_pos[1] - self.m3_mousepos[1]) // self.grid
            else:
                self.x_scroll -= self.x_scroll % self.grid
                self.y_scroll -= self.y_scroll % self.grid

                self.m3_mousepos = mouse_pos
        """

        self.save_to_list()
        return movement_type

    def change_place_type(self, event: pygame.event.Event):
        """use mouse wheel to change place type"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.place_type = (self.place_type % 5) + 1
            elif event.button == 5:  # Scroll down
                self.place_type = (self.place_type - 2) % 5 + 1

    # ===============================
    # DRAW GRID
    # ===============================
    def draw_grid(self, mouse_pos):
        width, height = self.screen.get_size()
        start_x = -self.x_scroll % self.grid
        for x in range(int(start_x) - self.grid, width + self.grid, self.grid):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, height))

        start_y = -self.y_scroll % self.grid
        for y in range(int(start_y) - self.grid, height + self.grid, self.grid):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (width, y))

        # Highlight tile
        mouse_x, mouse_y = mouse_pos
        world_x = mouse_x + self.x_scroll
        world_y = mouse_y + self.y_scroll
        grid_x = (world_x // self.grid) * self.grid - self.x_scroll
        grid_y = (world_y // self.grid) * self.grid - self.y_scroll
        pygame.draw.rect(self.screen, (120, 170, 255), pygame.Rect(grid_x, grid_y, self.grid, self.grid), 2)
        # Show transparent object preview
        skip = False
        match self.place_type:
            case 1: # Spike
                if self.spike_animation_timer.has_elapsed():
                    self.spike_img = (self.spike_img + 1) % len(self.spike_tex.images)
                    self.spike_animation_timer.reset()
                    self.spike_animation_timer.start()
                image = self.spike_tex.get_image(self.spike_img).convert_alpha()
            case 2: # Cube
                if self.cube_animation_timer.has_elapsed():
                    self.cube_img = (self.cube_img + 1) % len(self.cube_tex.images)
                    self.cube_animation_timer.reset()
                    self.cube_animation_timer.start()
                image = self.cube_tex.get_image(self.cube_img).convert_alpha()
            case 3: # Start
                skip = True
                image = pygame.Surface((self.grid, self.grid), pygame.SRCALPHA)
                pygame.draw.rect(image, (255, 255, 0, 128), (0, 0, self.grid, self.grid))
            case 4: # End
                if self.flag_animation_timer.has_elapsed():
                    self.flag_img = (self.flag_img + 1) % len(self.flag_tex.images)
                    self.flag_animation_timer.reset()
                    self.flag_animation_timer.start()
                image = self.flag_tex.get_image(self.flag_img).convert_alpha()
            case 5: # Player Spawn
                image = self.miss_tex.get_image(0).convert_alpha()
            case _: # Missing
                image = self.miss_tex.get_image(0).convert_alpha()
        if not skip:
            image.set_alpha(128) #50% transparency
        self.screen.blit(image, (grid_x, grid_y))  # pyright: ignore[reportArgumentType] #

        # Origin lines
        origin_screen_x = -self.x_scroll
        origin_screen_y = self.world_origin_y - self.y_scroll
        pygame.draw.line(self.screen, self.origin_color, (origin_screen_x, 0), (origin_screen_x, height), self.origin_thickness)
        pygame.draw.line(self.screen, self.origin_color, (0, origin_screen_y), (width, origin_screen_y), self.origin_thickness)

        # Draw selected object
        utility.render_text(f"Selected: {self.place_type_refrence[self.place_type]}",
                            (((width/2)-utility.scale(100, round_values= True)), utility.scale(10, round_values=True)),
                            utility.scale(50, round_values= True), surface=self.screen)  # pyright: ignore[reportArgumentType] #
        return (grid_x, grid_y)

    # ===============================
    # DRAW WORLD OBJECTS
    # ===============================
    def draw_grid_objects(self):
        for spike in self.objects["Spike"]:
            spike.draw(self.screen, self.x_scroll, self.y_scroll, debug=True)
        for block in self.objects["Block"]:
            if self.cube_animation_timer.has_elapsed():
                self.cube_img = (self.cube_img + 1) % len(self.cube_tex.images)
                self.cube_animation_timer.reset()
                self.cube_animation_timer.start()

            screen_rect = pygame.Rect(block.x - self.x_scroll, block.y - self.y_scroll, block.width, block.height)
            self.screen.blit(self.cube_tex.get_image(self.cube_img), screen_rect)  # pyright: ignore[reportArgumentType]

        pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(self.objects["Start"].x - self.x_scroll, self.objects["Start"].y - self.y_scroll, self.objects["Start"].width, self.objects["Start"].height)) # pyright: ignore[reportAttributeAccessIssue]

        if self.flag_animation_timer.has_elapsed():
            self.flag_animation_timer.reset()
            self.flag_animation_timer.start()
            self.flag_img = (self.flag_img + 1) % len(self.flag_tex.images) 

        self.screen.blit(self.flag_tex.get_image( self.flag_img), pygame.Rect(self.objects["End"].x - self.x_scroll, self.objects["End"].y - self.y_scroll, self.objects["End"].width, self.objects["End"].height)) # pyright: ignore[reportAttributeAccessIssue]

        if self.objects["PlayerSpawn"]:
            self.screen.blit(self.miss_tex.get_image(0), pygame.Rect(self.objects["PlayerSpawn"].x - self.x_scroll, self.objects["PlayerSpawn"].y - self.y_scroll, self.objects["PlayerSpawn"].width, self.objects["PlayerSpawn"].height))

    # ===============================
    # LOAD WORLD 
    # ===============================
    def get_world(self):
        for y, row in enumerate(reversed(self.level)):
            for x, block in enumerate(row):
                world_row = 11 - y
                world_x = x * self.grid
                world_y = world_row * self.grid

                if block == 1:
                    self.objects["Spike"].append(Spike(world_x, world_y, self.grid, side="Pointing Up"))
                elif block == 2:
                    self.objects["Block"].append(pygame.Rect(world_x, world_y, self.grid, self.grid))
                elif block == 5:
                    self.objects["Spike"].append(Spike(world_x, world_y, self.grid, side="Pointing Right"))
                elif block == 6:
                    self.objects["Spike"].append(Spike(world_x, world_y, self.grid, side="Pointing Down"))
                elif block == 7:
                    self.objects["Spike"].append(Spike(world_x, world_y, self.grid, side="Pointing Left"))
        # get the distance from the start to te flag
        self.level_dist = (self.get_start_point().x) + (self.objects["End"].x) + 400

    def get_start_block(self):
        best_x, best_y = 0,0 
        for y, layer in enumerate(reversed(self.level)):
            for x, element in enumerate(layer):
                match element:
                    case 0:
                        continue
                    case _:
                        if best_x > x: best_x = x
                        if best_y > y: best_y = y

        return pygame.Vector2(best_x, best_y)
                
                    

                    
    # ===============================
    # SAVE WORLD TO LIST (DYNAMIC BOUNDS)
    # ===============================
    def save_to_list(self):
        
        spikes = self.objects["Spike"]
        blocks = self.objects["Block"]
         
        if not spikes and not blocks:
            self.level = []
            return

        # 1. Find bounds
        all_x = [obj.x for obj in spikes] + [obj.x for obj in blocks] + [self.objects["Start"].x, self.objects["End"].x]
        all_y = [obj.y for obj in spikes] + [obj.y for obj in blocks] + [self.objects["Start"].y, self.objects["End"].y]

        min_x, max_x = 0, max(all_x)
        min_y, max_y = min(all_y), max(all_y)


        # 2. Convert to grid coordinates
        grid_min_x = 0
        grid_max_x = int(max_x // self.grid)
        grid_min_y = int(min_y // self.grid)
        grid_max_y = int(max_y // self.grid)

        width = grid_max_x - grid_min_x + 1
        height = grid_max_y - grid_min_y + 1

        # 3. Create empty 2D list
        new_level = [[0 for _ in range(width)] for _ in range(height)]

        # 4. Place spikes
        for spike in spikes:
            gx = int(spike.x // self.grid) - grid_min_x
            gy = int(spike.y // self.grid) - grid_min_y
            
            val = 1
            if spike.type == "Pointing Right": val = 5
            elif spike.type == "Pointing Down": val = 6
            elif spike.type == "Pointing Left": val = 7
            new_level[height - 1 - gy][gx] = val

        # 5. Place blocks
        for block in blocks:
            gx = int(block.x // self.grid) - grid_min_x
            gy = int(block.y // self.grid) - grid_min_y
            new_level[height - 1 - gy][gx] = 2

        # 6. Set main level list
        self.level = list(reversed(new_level))

    def get_start_pos_x(self):
        min_x = float('inf')
        if self.objects["Block"]:
            min_x = min(min_x, min(b.x for b in self.objects["Block"]))
        if self.objects["Spike"]:
            min_x = min(min_x, min(s.x for s in self.objects["Spike"]))
            
        if min_x == float('inf'):
            return self.objects["Start"].x
        return min_x

    def get_start_point(self):
        return self.objects["PlayerSpawn"] if self.objects["PlayerSpawn"] else self.objects["Start"]

    # ===============================
    # UPDATE WORLD (PLAY MODE)
    # ===============================
    def update_world(self, speed, player_hitbox, debug):
        if self.editor:
            return False

        self.x_scroll += speed
        print(speed)

        start_x = self.get_start_point().x
        end_x = self.objects["End"].x + self.objects["End"].width
        self.level_completion = round((self.x_scroll/(self.level_dist)) * 100) + 15

        #update flag tex
        if self.flag_animation_timer.has_elapsed():
            self.flag_animation_timer.reset()
            self.flag_animation_timer.start()
            self.flag_img = (self.flag_img + 1) % len(self.flag_tex.images)

        self.screen.blit(self.flag_tex.get_image(0),
                         pygame.Rect(self.objects["End"].x - self.x_scroll, self.objects["End"].y - self.y_scroll,
                                     self.objects["End"].width, self.objects["End"].height))
        # Draw spikes within start-end bounds
        for spike in self.objects["Spike"]:
            if start_x <= spike.x <= end_x:
                spike.draw(self.screen, self.x_scroll, self.y_scroll, debug)

        # Draw blocks within start-end bounds
        for block in self.objects["Block"]:
            if start_x <= block.x <= end_x:
                if self.cube_animation_timer.has_elapsed():
                    self.cube_img = (self.cube_img + 1) % len(self.cube_tex.images)
                    self.cube_animation_timer.reset()
                    self.cube_animation_timer.start()
                screen_rect = pygame.Rect(block.x - self.x_scroll, block.y - self.y_scroll, block.width, block.height)
                self.screen.blit(self.cube_tex.get_image(self.cube_img), screen_rect)  # pyright: ignore[reportArgumentType]

                if debug:
                    # Draw the Side and bottom hitbox, the kill hitbox, and then the top hitbox for standing on it
                    pygame.draw.rect(self.screen, (255, 0, 0), screen_rect, 1)  # Red = collision box
                    pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(screen_rect.x, screen_rect.y + screen_rect.height//2, screen_rect.width, screen_rect.height//2), 1)  # Green = kill box
                    pygame.draw.rect(self.screen, (0, 0, 255), pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, screen_rect.height//2), 1)  # Blue = top box for standing


        # Collision (only for objects within bounds)
        for spike in self.objects["Spike"]:
            if start_x <= spike.x <= end_x:
                # The player_hitbox is in screen coordinates, but the spike's geometry is in world coordinates.
                # We must perform the collision check in the same coordinate space. Here, we'll use screen space.

                # 1. Broad-phase check: Use the spike's bounding box, converted to screen coordinates.
                spike_screen_bbox = pygame.Rect(spike.x - self.x_scroll, spike.y - self.y_scroll, spike.size, spike.size)
                if not player_hitbox.colliderect(spike_screen_bbox):
                    spike.color = (255, 0, 0)
                    continue  # Not close, so no collision. Check the next spike.

                # 2. Narrow-phase check: More precise triangle-to-rectangle collision.
                screen_verts = [(vx - self.x_scroll, vy - self.y_scroll) for vx, vy in spike.vert]
                lines = [(screen_verts[0], screen_verts[1]), (screen_verts[1], screen_verts[2]), (screen_verts[2], screen_verts[0])]
                collided = any(player_hitbox.clipline(line) for line in lines) or player_hitbox.collidepoint(screen_verts[0])

                if collided:
                    spike.color = (0, 255, 0)
                    return True
                else:
                    spike.color = (255, 0, 0)

        return False

    def cube_collition(self, player: pygame.Rect, velocity_y: float):
        """
        Returns:
            on_cube (bool)  -> Player landed on top
            level (int)     -> Y level to snap player to
            dead (bool)     -> Player hit side or bottom
        """
        start_x = self.objects["Start"].x
        end_x = self.objects["End"].x + self.objects["End"].width

        for block in self.objects["Block"]:
            if start_x <= block.x <= end_x:
                screen_rect = pygame.Rect(block.x - self.x_scroll, block.y - self.y_scroll, block.width, block.height)
                kill_box = pygame.Rect(screen_rect.x, screen_rect.y + screen_rect.height//2, screen_rect.width, screen_rect.height//2)  # Green = kill box
                standing = pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, screen_rect.height//2) # Blue = top box for standing
                if player.colliderect(kill_box):
                    return False, None, True
                elif player.colliderect(standing) and velocity_y >= 0:
                    return True, screen_rect.y, False
        return False, None, False

    # ===============================
    # Get the saved world data in a dict format for saving to JSON
    # ===============================
    def load_from_dict(self, data: dict):
        """
        Load the editor state from a dictionary (like JSON).
        Restores spikes, blocks, start/end, and level map.
        """
        self.editor = data.get("editor", False)
        self.x_scroll = data.get("x_scroll", -self.screen.get_width() // 2)
        self.y_scroll = data.get("y_scroll", 0)

        objects_data = data.get("objects", {})

        # Clear objects (they will be rebuilt from the map via get_world)
        self.objects["Spike"] = []
        self.objects["Block"] = []

        # Load Start & End
        start_data = objects_data.get("Start", [0, self.world_origin_y, self.grid, self.grid])
        end_data = objects_data.get("End", [self.grid * 100, self.world_origin_y, self.grid, self.grid])
        self.objects["Start"] = pygame.Rect(*start_data)
        self.objects["End"] = pygame.Rect(*end_data)
        ps_data = objects_data.get("PlayerSpawn", None)
        self.objects["PlayerSpawn"] = pygame.Rect(*ps_data) if ps_data else None

        # Load map
        self.level = data.get("map", [])

        # Optional: Recalculate world objects if needed
        self.get_world()


    # ===============================
    # RESET
    # ===============================
    def reset(self):
        self.objects["Spike"] = []
        self.objects["Block"] = []
        self.get_world()
        self.x_scroll = self.get_start_point().x - (self.grid * 7)
        self.y_scroll = 0
    
    def set_level(self, level):
        self.level = level
        self.reset()  # Reset camera and objects to reflect new level

    def end(self, player: pygame.Rect ):

        if pygame.Rect(self.objects["End"].x - self.x_scroll, self.objects["End"].y - self.y_scroll, self.objects["End"].width, self.objects["End"].height).colliderect(player):
            return True
        return False




    def __dict__(self):
        # Helper to convert pygame.Rect to list
        rect_to_list = lambda r: [r.x, r.y, r.width, r.height]

        # Helper to convert Spike to dict (position + size)
        spike_to_dict = lambda s: {"x": s.x, "y": s.y, "size": s.size}

        return {
            "editor": self.editor,
            "x_scroll": self.x_scroll,
            "y_scroll": self.y_scroll,
            "objects": {
                "Spike": [spike_to_dict(spike) for spike in self.objects["Spike"]],
                "Block": [rect_to_list(block) for block in self.objects["Block"]],
                "Start": rect_to_list(self.objects["Start"]),
                "End": rect_to_list(self.objects["End"]),
                "PlayerSpawn": rect_to_list(self.objects["PlayerSpawn"]) if self.objects["PlayerSpawn"] else None
            },
            "map": self.level
        }

    def __str__(self):
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x = mouse_x + self.x_scroll
        world_y = mouse_y + self.y_scroll
        grid_x = (world_x // self.grid) * self.grid - self.x_scroll
        grid_y = (world_y // self.grid) * self.grid - self.y_scroll


        return f"""
        Editor: {self.editor}
        Camera Scroll: ({self.x_scroll}, {self.y_scroll})
        Mouse Grid Position: ({grid_x}, {grid_y})
        Spikes: {len(self.objects['Spike'])}
        Blocks: {len(self.objects['Block'])}
        """


class Spike:

    def __init__(self, x, y, size, side="Pointing Up"):
        """
        x, y: top-left corner of the spike's bounding box
        size: width and height of the spike (assumed to be square)
        side: "Pointing Up", "Pointing Down", "Pointing Left", "Pointing Right"
        """
        self.x = x
        self.y = y
        self.size = size
        self.type = side
        self.color = (255, 0, 0)
        
        # spike tex
        self.spike_tex = utility.SpriteSheet()
        self.spike_tex.extract_grid(path="Textures/Spike.png", crop_size=(16, 16), scale=(size, size),
                                    alpha=255)
        self.spike_animation_timer = utility.Timer(0.04)
        self.spike_animation_timer.start()
        self.spike_img = 0

        self.update_geometry()

    def update_geometry(self):


        match self.type:
            case "Pointing Up":
                self.vert = [
                    [self.x + self.size // 2, self.y],
                    [self.x, self.y + self.size],
                    [self.x + self.size, self.y + self.size],
                ]
            case "Pointing Down":
                self.vert = [
                    [self.x, self.y],
                    [self.x + self.size // 2, self.y + self.size],
                    [self.x + self.size, self.y],
                   
                ]
                self.spike_tex.rotate_images(180)
            case "Pointing Left":
                self.vert = [
                    [self.x, self.y + self.size // 2],
                    [self.x, self.y],
                    [self.x, self.y + self.size],
                ]
                self.spike_tex.rotate_images(90)
            case "Pointing Right":
                self.vert = [
                    [self.x + self.size, self.y + self.size // 2],
                    [self.x + self.size, self.y],
                    [self.x + self.size, self.y + self.size],
                ]
                self.spike_tex.rotate_images(270)
            case _:
                raise ValueError("This side doesn't exist")

        self.collision_rect = self.create_collision_rect()

    def create_collision_rect(self):
        p1, p2, p3 = self.vert
        mp1 = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        mp2 = ((p1[0] + p3[0]) // 2, (p1[1] + p3[1]) // 2)
        d1 = abs(mp1[0] - mp2[0])
        d2 = abs(mp1[1] - p3[1])
        return pygame.Rect(mp1[0], mp1[1], d1, d2)

    def draw(self, screen, x_scroll, y_scroll, debug):
        screen_verts = [(vx - x_scroll, vy - y_scroll) for vx, vy in self.vert]


        screen.blit(self.spike_tex.get_image(self.spike_img), (self.x - x_scroll, self.y - y_scroll))
        #pygame.draw.polygon(screen, (255, 255, 255), screen_verts)
        if self.spike_animation_timer.has_elapsed():
            self.spike_img = (self.spike_img + 1) % len(self.spike_tex.images)
            self.spike_animation_timer.reset()
            self.spike_animation_timer.start()

        if debug:
            pygame.draw.circle(screen, (255, 0, 0), screen_verts[0], 3)
            pygame.draw.circle(screen, (0, 255, 0), screen_verts[1], 3)
            pygame.draw.circle(screen, (0, 0, 255), screen_verts[2], 3)
            debug_rect = pygame.Rect(self.collision_rect.x - x_scroll, self.collision_rect.y - y_scroll, self.collision_rect.width, self.collision_rect.height)
            pygame.draw.rect(screen, self.color, debug_rect, 1)

    def check_collition(self, hitbox: pygame.Rect, rect_to_rect: bool = False) -> bool:
        """
        if rect_to_rect:
            return hitbox.colliderect(self.collision_rect)
        spike_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        if not hitbox.colliderect(spike_rect):
            return False
        lines = [(self.vert[0], self.vert[1]), (self.vert[1], self.vert[2]), (self.vert[2], self.vert[0])]
        for start, end in lines:
            if hitbox.clipline(start, end):
                return True
        return hitbox.collidepoint(self.vert[0])
        """
        return self.collision_rect.colliderect(hitbox)

    def __str__(self):
        return f"Spike: {self.vert}, Collision Rect: {self.collision_rect}, Type: {self.type}"