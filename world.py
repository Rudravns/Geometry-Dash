import pygame
import math
import utility

class Editor:

    def __init__(self, level, editor, ground_y):
        self.screen = pygame.display.get_surface()
        self.movement_timer = utility.Timer(0.1)
        self.movement_timer.start()

        # Editor state
        self.editor = editor
        self.editor_window = True
        self.place_type = 1  # 1 for spike, 2 for block

        # Grid
        self.grid = 40
        self.grid_color = (70, 70, 70)
        self.origin_color = (255, 60, 60)
        self.origin_thickness = 4

        # Camera (origin centered)
        width, height = self.screen.get_size()
        self.x_scroll = -width // 2
        self.y_scroll = 0

        # World
        self.level = level
        self.world_origin_y = ground_y

        # World objects (WORLD COORDS)
        self.objects = {
            "Spike": [],
            "Block": [],
            "Start": pygame.Rect(0, 440, self.grid, self.grid),
            "End": pygame.Rect(4240, 440, self.grid, self.grid),
            
        }

        #init textures
        self.cube_tex = utility.SpriteSheet()
        self.cube_tex.extract_grid(path="Textures/Cube.png", crop_size=(16,16), scale=(self.grid, self.grid), alpha=255)
        self.cube_animation_timer = utility.Timer(0.1)
        self.cube_animation_timer.start()
        self.cube_img = 0



        self.get_world()

    # ===============================
    # EDITOR UPDATE
    # ===============================
    def level_editor(self):
        keys = pygame.key.get_pressed()
        movement_type = [0,0,0,0]

        if self.movement_timer.has_elapsed():

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x_scroll -= self.grid
                movement_type[2] = 1

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x_scroll += self.grid
                movement_type[3] = 1

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y_scroll -= self.grid
                movement_type[0] = 1

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y_scroll += self.grid
                movement_type[1] = 1

            if keys[pygame.K_1]:
                self.place_type = 1
            if keys[pygame.K_2]:
                self.place_type = 2
            if keys[pygame.K_3]:
                self.place_type = 3
            if keys[pygame.K_4]:
                self.place_type = 4


            self.movement_timer.reset()
            self.movement_timer.start()

        # draw the grid and objects
        self.draw_grid_objects()
        mouse_pos = self.draw_grid()
        mouse_down = pygame.mouse.get_pressed()

        if mouse_down[0]:
            world_x = mouse_pos[0] + self.x_scroll
            world_y = mouse_pos[1] + self.y_scroll
            grid_x = (world_x // self.grid) * self.grid
            grid_y = (world_y // self.grid) * self.grid

            new_rect = pygame.Rect(grid_x, grid_y, self.grid, self.grid)

            if self.place_type == 1:  # Spike
                # Prevent overlap with any block, spike, start, or end
                if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                and not new_rect.colliderect(self.objects["Start"]) \
                and not new_rect.colliderect(self.objects["End"]) \
                and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                    self.objects["Spike"].append(Spike(grid_x, grid_y, self.grid))

            elif self.place_type == 2:  # Block
                # Prevent overlap with spikes, start, or end
                if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                and not new_rect.colliderect(self.objects["Start"]) \
                and not new_rect.colliderect(self.objects["End"]) \
                and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                    self.objects["Block"].append(new_rect)

            elif self.place_type == 3:  # Start
                # Move start only if not colliding with blocks or spikes
                if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                    self.objects["Start"].x = grid_x
                    self.objects["Start"].y = grid_y

            elif self.place_type == 4:  # End
                # Move end only if not colliding with blocks or spikes
                if not any(spike.check_collition(new_rect, rect_to_rect=True) for spike in self.objects["Spike"]) \
                and not any(block.colliderect(new_rect) for block in self.objects["Block"]):
                    self.objects["End"].x = grid_x
                    self.objects["End"].y = grid_y
            

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
                    break

        self.save_to_list()
        return movement_type

    # ===============================
    # DRAW GRID
    # ===============================
    def draw_grid(self):
        width, height = self.screen.get_size()
        start_x = -self.x_scroll % self.grid
        for x in range(int(start_x) - self.grid, width + self.grid, self.grid):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, height))

        start_y = -self.y_scroll % self.grid
        for y in range(int(start_y) - self.grid, height + self.grid, self.grid):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (width, y))

        # Highlight tile
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x = mouse_x + self.x_scroll
        world_y = mouse_y + self.y_scroll
        grid_x = (world_x // self.grid) * self.grid - self.x_scroll
        grid_y = (world_y // self.grid) * self.grid - self.y_scroll
        pygame.draw.rect(self.screen, (120, 170, 255), pygame.Rect(grid_x, grid_y, self.grid, self.grid), 2)

        # Origin lines
        origin_screen_x = -self.x_scroll
        origin_screen_y = self.world_origin_y - self.y_scroll
        pygame.draw.line(self.screen, self.origin_color, (origin_screen_x, 0), (origin_screen_x, height), self.origin_thickness)
        pygame.draw.line(self.screen, self.origin_color, (0, origin_screen_y), (width, origin_screen_y), self.origin_thickness)

        # Draw selected object
        utility.render_text(f"Selected: {utility.map_key[self.place_type]}",
                            (((width/2)-utility.scale(100, round_values= True)), utility.scale(10, round_values=True)), 
                            utility.scale(50, round_values= True))  # pyright: ignore[reportArgumentType] #
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
            self.screen.blit(self.cube_tex.get_image(self.cube_img).convert_alpha(), screen_rect)  # pyright: ignore[reportArgumentType]

        pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(self.objects["Start"].x - self.x_scroll, self.objects["Start"].y - self.y_scroll, self.objects["Start"].width, self.objects["Start"].height)) # pyright: ignore[reportAttributeAccessIssue]
        pygame.draw.rect(self.screen, (255, 0, 255), pygame.Rect(self.objects["End"].x - self.x_scroll, self.objects["End"].y - self.y_scroll, self.objects["End"].width, self.objects["End"].height)) # pyright: ignore[reportAttributeAccessIssue]
    # ===============================
    # LOAD WORLD 
    # ===============================
    def get_world(self):
        total_rows = len(self.level)
        for y, row in enumerate(reversed(self.level)):
            for x, block in enumerate(row):
                world_row = 11 - y
                world_x = x * self.grid
                world_y = world_row * self.grid

                if block == 1:
                    self.objects["Spike"].append(Spike(world_x, world_y, self.grid))
                elif block == 2:
                    self.objects["Block"].append(pygame.Rect(world_x, world_y, self.grid, self.grid))

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

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)


        # 2. Convert to grid coordinates
        grid_min_x = min_x // self.grid
        grid_max_x = max_x // self.grid
        grid_min_y = min_y // self.grid
        grid_max_y = max_y // self.grid

        width = grid_max_x - grid_min_x + 1
        height = grid_max_y - grid_min_y + 1

        # 3. Create empty 2D list
        new_level = [[0 for _ in range(width)] for _ in range(height)]

        # 4. Place spikes
        for spike in spikes:
            gx = spike.x // self.grid - grid_min_x
            gy = spike.y // self.grid - grid_min_y
            new_level[height - 1 - gy][gx] = 1

        # 5. Place blocks
        for block in blocks:
            gx = block.x // self.grid - grid_min_x
            gy = block.y // self.grid - grid_min_y
            new_level[height - 1 - gy][gx] = 2

        # 6. Set main level list
        self.level = list(reversed(new_level))

    # ===============================
    # UPDATE WORLD (PLAY MODE)
    # ===============================
    def update_world(self, speed, player_hitbox, debug):
        if self.editor:
            return False

        self.x_scroll += speed

        start_x = self.objects["Start"].x
        end_x = self.objects["End"].x + self.objects["End"].width

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
                self.screen.blit(self.cube_tex.get_image(self.cube_img).convert_alpha(), screen_rect)  # pyright: ignore[reportArgumentType]

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

        # Load Spikes
        self.objects["Spike"] = []
        for spike_data in objects_data.get("Spike", []):
            x = spike_data.get("x", 0)
            y = spike_data.get("y", 0)
            size = spike_data.get("size", self.grid)
            self.objects["Spike"].append(Spike(x, y, size))

        # Load Blocks
        self.objects["Block"] = []
        for block_data in objects_data.get("Block", []):
            if len(block_data) == 4:
                rect = pygame.Rect(block_data[0], block_data[1], block_data[2], block_data[3])
                self.objects["Block"].append(rect)

        # Load Start & End
        start_data = objects_data.get("Start", [0, self.world_origin_y, self.grid, self.grid])
        end_data = objects_data.get("End", [self.grid * 100, self.world_origin_y, self.grid, self.grid])
        self.objects["Start"] = pygame.Rect(*start_data)
        self.objects["End"] = pygame.Rect(*end_data)

        # Load map
        self.level = data.get("map", [])

        # Optional: Recalculate world objects if needed
        self.get_world()


    # ===============================
    # RESET
    # ===============================
    def reset(self):
        self.x_scroll = -self.screen.get_width() // 2
        self.y_scroll = 0
        self.objects["Spike"] = []
        self.objects["Block"] = []
        self.get_world()
    
    def set_level(self, level):
        self.level = level
        self.reset()  # Reset camera and objects to reflect new level


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
                "End": rect_to_list(self.objects["End"])
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

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.color = (255, 0, 0)
        self.update_geometry()

    def update_geometry(self):
        self.vert = [
            [self.x + self.size // 2, self.y],
            [self.x, self.y + self.size],
            [self.x + self.size, self.y + self.size],
        ]
        self.collision_rect = self.create_collision_rect()

    def create_collision_rect(self):
        p1, p2, p3 = self.vert
        midpoint1 = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        midpoint2 = ((p1[0] + p3[0]) // 2, (p1[1] + p3[1]) // 2)
        distance1 = abs(midpoint1[0] - midpoint2[0])
        distance2 = abs(midpoint1[1] - p3[1])
        return pygame.Rect(midpoint1[0], midpoint1[1], distance1, distance2)

    def draw(self, screen, x_scroll, y_scroll, debug):
        screen_verts = [(vx - x_scroll, vy - y_scroll) for vx, vy in self.vert]
        pygame.draw.polygon(screen, (255, 255, 255), screen_verts)
        if debug:
            pygame.draw.circle(screen, (255, 0, 0), screen_verts[0], 3)
            pygame.draw.circle(screen, (0, 255, 0), screen_verts[1], 3)
            pygame.draw.circle(screen, (0, 0, 255), screen_verts[2], 3)
            debug_rect = pygame.Rect(self.collision_rect.x - x_scroll, self.collision_rect.y - y_scroll, self.collision_rect.width, self.collision_rect.height)
            pygame.draw.rect(screen, self.color, debug_rect, 1)

    def check_collition(self, hitbox: pygame.Rect, rect_to_rect: bool = False) -> bool:
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

    def __str__(self):
        return f"Spike: {self.vert}, Collision Rect: {self.collision_rect}"