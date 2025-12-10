import pygame
import os
from ui.theme import Theme

class IsometricCamera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scroll_x = 0
        self.scroll_y = 0
        # Zoom level? For now 1.0
        
    def cart_to_iso(self, cart_x, cart_y):
        # Isometric projection:
        # iso_x = (cart_x - cart_y)
        # iso_y = (cart_x + cart_y) / 2
        iso_x = (cart_x - cart_y)
        iso_y = (cart_x + cart_y) / 2
        return iso_x, iso_y

    def apply(self, x, y):
        iso_x, iso_y = self.cart_to_iso(x, y)
        return iso_x + self.width // 2 + self.scroll_x, iso_y + self.height // 4 + self.scroll_y

    def screen_to_iso(self, screen_x, screen_y):
        # Reverse the apply + cart_to_iso transformation
        # 1. Remove offset
        iso_x = screen_x - (self.width // 2 + self.scroll_x)
        iso_y = screen_y - (self.height // 4 + self.scroll_y)
        
        # 2. Reverse projection
        # iso_x = cart_x - cart_y
        # iso_y = (cart_x + cart_y) / 2  =>  2*iso_y = cart_x + cart_y
        #
        # (2*iso_y + iso_x) = 2*cart_x  =>  cart_x = (2*iso_y + iso_x) / 2
        # (2*iso_y - iso_x) = 2*cart_y  =>  cart_y = (2*iso_y - iso_x) / 2
        
        cart_x = (2 * iso_y + iso_x) / 2
        cart_y = (2 * iso_y - iso_x) / 2
        
        return cart_x, cart_y

class WorldRenderer:
    def __init__(self, screen, tile_size=64): # Increased tile size for assets
        self.screen = screen
        self.tile_size = tile_size
        self.camera = IsometricCamera(screen.get_width(), screen.get_height())
        
        self.assets = {}
        self.load_assets()
    
    def trim_transparent_borders(self, surface):
        """Remove transparent borders from a surface"""
        # Get the bounding box of non-transparent pixels
        rect = surface.get_bounding_rect()
        
        if rect.width == 0 or rect.height == 0:
            # Image is completely transparent, return as-is
            return surface
        
        # Create a new surface with just the non-transparent content  
        trimmed = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        trimmed.blit(surface, (0, 0), rect)
        return trimmed
        
    def load_assets(self):
        # Use absolute path relative to this file to ensure assets load from anywhere
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asset_dir = os.path.join(base_dir, "assets")
        # Load tiles
        try:
            self.assets['grass'] = pygame.image.load(os.path.join(asset_dir, "iso_grass_1763665136323.png")).convert_alpha()
            self.assets['soil'] = pygame.image.load(os.path.join(asset_dir, "iso_soil_1763665149140.png")).convert_alpha()
            
            # Load Machine Assets
            self.assets['Wind Turbine'] = pygame.image.load(os.path.join(asset_dir, "iso_wind_turbine.png")).convert_alpha()
            self.assets['Rain Collector'] = pygame.image.load(os.path.join(asset_dir, "iso_rain_collector.png")).convert_alpha()
            self.assets['Solar Panel'] = pygame.image.load(os.path.join(asset_dir, "iso_solar_panel.png")).convert_alpha()
            self.assets['Heater'] = pygame.image.load(os.path.join(asset_dir, "iso_heater.png")).convert_alpha()
            self.assets['Battery'] = pygame.image.load(os.path.join(asset_dir, "iso_battery.png")).convert_alpha()
            self.assets['Water Tank'] = pygame.image.load(os.path.join(asset_dir, "iso_water_tank.png")).convert_alpha()
            self.assets['Sprinkler'] = pygame.image.load(os.path.join(asset_dir, "iso_sprinkler.png")).convert_alpha()
            self.assets['Winter Wheat'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_wheat.png")).convert_alpha()
            self.assets['Corn'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_corn.png")).convert_alpha()
            self.assets['Potato'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_potato.png")).convert_alpha()
            self.assets['Rice'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_rice.png")).convert_alpha()
            self.assets['Cactus'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_cactus.png")).convert_alpha()
            self.assets['Sunflower'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_sunflower.png")).convert_alpha()
            self.assets['Harvester'] = pygame.image.load(os.path.join(asset_dir, "iso_harvester.png")).convert_alpha()
            
            # Growth stage assets
            self.assets['Winter Wheat_stage0'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_wheat_stage0.png")).convert_alpha()
            self.assets['Winter Wheat_stage1'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_wheat_stage1.png")).convert_alpha()
            self.assets['Corn_stage0'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_corn_stage0.png")).convert_alpha()
            self.assets['Corn_stage1'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_corn_stage1.png")).convert_alpha()
            self.assets['Potato_stage0'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_potato_stage0.png")).convert_alpha()
            self.assets['Potato_stage1'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_potato_stage1.png")).convert_alpha()
            self.assets['Rice_stage0'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_rice_stage0.png")).convert_alpha()
            self.assets['Rice_stage1'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_rice_stage1.png")).convert_alpha()
            self.assets['Cactus_stage0'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_cactus_stage0.png")).convert_alpha()
            self.assets['Cactus_stage1'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_cactus_stage1.png")).convert_alpha()
            self.assets['Sunflower_stage0'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_sunflower_stage0.png")).convert_alpha()
            self.assets['Sunflower_stage1'] = pygame.image.load(os.path.join(asset_dir, "iso_crop_sunflower_stage1.png")).convert_alpha()
            
            # Terrain biome tiles
            self.assets['terrain_water'] = pygame.image.load(os.path.join(asset_dir, "iso_terrain_water.png")).convert_alpha()
            self.assets['terrain_sand'] = pygame.image.load(os.path.join(asset_dir, "iso_terrain_sand.png")).convert_alpha()
            self.assets['terrain_forest'] = pygame.image.load(os.path.join(asset_dir, "iso_terrain_forest.png")).convert_alpha()
            self.assets['terrain_rock'] = pygame.image.load(os.path.join(asset_dir, "iso_terrain_rock.png")).convert_alpha()
            self.assets['terrain_snow'] = pygame.image.load(os.path.join(asset_dir, "iso_terrain_snow.png")).convert_alpha()
            
            # Creature Assets
            self.assets['Petrichor Slime'] = pygame.image.load(os.path.join(asset_dir, "iso_creature_petrichor_slime.png")).convert_alpha()
            self.assets['Fulgarite Golem'] = pygame.image.load(os.path.join(asset_dir, "iso_creature_fulgarite_golem.png")).convert_alpha()
            self.assets['Thermal Kite'] = pygame.image.load(os.path.join(asset_dir, "iso_creature_thermal_kite.png")).convert_alpha()
            self.assets['Nebula Moth'] = pygame.image.load(os.path.join(asset_dir, "iso_creature_nebula_moth.png")).convert_alpha()
            self.assets['Frost Wisp'] = pygame.image.load(os.path.join(asset_dir, "iso_creature_frost_wisp.png")).convert_alpha()
            self.assets['Creature Stable'] = pygame.image.load(os.path.join(asset_dir, "iso_creature_stable.png")).convert_alpha()
            
            # Trim transparent borders from all assets EXCEPT terrain tiles
            # (terrain tiles need to maintain their dimensions for proper isometric alignment)
            # TEMPORARILY DISABLED - investigating checkered tile issue
            # terrain_tiles = ['grass', 'soil', 'terrain_water', 'terrain_sand', 'terrain_forest', 'terrain_rock', 'terrain_snow']
            # for key in list(self.assets.keys()):
            #     if self.assets[key] is not None and key not in terrain_tiles:
            #         self.assets[key] = self.trim_transparent_borders(self.assets[key])
            
            # Scale tiles if needed. Assuming generated images are large.
            # Let's scale them to tile_size * 2 width (since iso tiles are wide)
            target_w = self.tile_size * 2
            
            for key in ['grass', 'soil']:
                img = self.assets[key]
                # Maintain aspect ratio
                aspect = img.get_height() / img.get_width()
                target_h = int(target_w * aspect)
                self.assets[key] = pygame.transform.scale(img, (target_w, target_h))
                
            # Scale machines to fit tile
            # They should probably be similar width to tiles, maybe a bit narrower/taller
            machine_w = self.tile_size * 1.5
            for key in ['Wind Turbine', 'Rain Collector', 'Solar Panel', 'Heater', 'Battery', 'Water Tank', 'Sprinkler', 'Creature Stable',
                        'Winter Wheat', 'Corn', 'Potato', 'Rice', 'Cactus', 'Sunflower', 'Harvester', 
                        'Winter Wheat_stage0', 'Winter Wheat_stage1', 
                        'Corn_stage0', 'Corn_stage1', 
                        'Potato_stage0', 'Potato_stage1', 
                        'Rice_stage0', 'Rice_stage1', 
                        'Cactus_stage0', 'Cactus_stage1', 
                        'Sunflower_stage0', 'Sunflower_stage1', 
                        'terrain_water', 'terrain_sand', 'terrain_forest', 'terrain_rock', 'terrain_snow',
                        'Petrichor Slime', 'Fulgarite Golem', 'Thermal Kite', 'Nebula Moth', 'Frost Wisp']:
                if key in self.assets:
                    img = self.assets[key]
                    aspect = img.get_height() / img.get_width()
                    target_h = int(machine_w * aspect)
                    self.assets[key] = pygame.transform.scale(img, (int(machine_w), target_h))
                
        except (pygame.error, FileNotFoundError) as e:
            print(f"Failed to load assets: {e}")
            # Fallback to colored surfaces
            if 'grass' not in self.assets: self.assets['grass'] = None
            if 'soil' not in self.assets: self.assets['soil'] = None

    def render(self, terrain_map):
        if not terrain_map:
            return
            
        rows = len(terrain_map)
        cols = len(terrain_map[0])
        
        half_w = self.tile_size
        half_h = self.tile_size // 2
        
        # 1. Render Island Base (Depth)
        # Thicker base with jagged edges
        depth_layers = 15
        layer_offset = 10
        
        soil_img = self.assets.get('soil')
        grass_img = self.assets.get('grass')
        
        # Center the map on screen
        # We can adjust camera scroll, or just rely on camera.apply() if it centers 0,0?
        # IsometricCamera centers (0,0) at screen center? No, it centers based on width/height.
        # Let's rely on the camera class for now.
        
        for y in range(rows):
            for x in range(cols):
                tile = terrain_map[y][x]
                screen_x, screen_y = self.camera.apply(x * half_w, y * half_w)
                
                # Draw Depth Layers
                if soil_img:
                    for d in range(depth_layers, 0, -1):
                        # Jagged Logic:
                        # Taper the island as it goes deeper.
                        # Simple cone/pyramid shape:
                        # If depth > X, only draw if not on edge.
                        
                        should_draw = True
                        if d > 5:
                            # Erode 1 tile ring every 3 layers?
                            erosion = (d - 5) // 3
                            if x < erosion or x >= cols - erosion or y < erosion or y >= rows - erosion:
                                should_draw = False
                                
                        # Add some noise?
                        if should_draw:
                             # Offset downwards
                            dy = screen_y + d * layer_offset
                            dest_x = screen_x - half_w
                            dest_y = dy
                            self.screen.blit(soil_img, (dest_x, dest_y))
                
                # Draw Surface Tile - Select based on biome
                # Biome mapping to terrain assets
                biome_to_asset = {
                    "WATER": "terrain_water",
                    "SAND": "terrain_sand",
                    "GRASS": "grass",
                    "FOREST": "terrain_forest",
                    "ROCK": "terrain_rock",
                    "SNOW": "terrain_snow"
                }
                
                terrain_key = biome_to_asset.get(tile.biome, "grass")
                terrain_img = self.assets.get(terrain_key, grass_img)
                
                if terrain_img:
                    dest_x = screen_x - half_w
                    dest_y = screen_y
                    self.screen.blit(terrain_img, (dest_x, dest_y))
                else:
                    # Fallback
                    pts = [
                        (screen_x, screen_y),
                        (screen_x + half_w, screen_y + half_h),
                        (screen_x, screen_y + 2 * half_h),
                        (screen_x - half_w, screen_y + half_h)
                    ]
                    pygame.draw.polygon(self.screen, tile.color, pts)
                    pygame.draw.polygon(self.screen, (0,0,0), pts, 1)

    def render_objects(self, game_state, dt=0):
        half_w = self.tile_size
        
        # Draw Harvester
        self.draw_harvester(5, 5, dt)

        # Draw Machines
        for machine in game_state.machines:
            self.draw_machine(machine, dt)

        for crop in game_state.crops:
            screen_x, screen_y = self.camera.apply(crop.x * half_w, crop.y * half_w)
            
            center_x = int(screen_x)
            center_y = int(screen_y) 
            
            # Try to get stage-specific asset first
            stage_asset_key = f"{crop.type.name}_stage{min(crop.stage, 2)}"
            asset = self.assets.get(stage_asset_key)
            
            if not asset:
                # Fallback to main asset (mature)
                asset = self.assets.get(crop.type.name)
            
            if asset:
                # Asset width/height
                aw, ah = asset.get_size()
                
                dest_x = center_x - aw // 2
                dest_y = center_y - ah + self.tile_size // 2
                
                self.screen.blit(asset, (dest_x, dest_y))
            else:
                # Fallback to primitive rendering if NO asset found at all
                if crop.type.name == "Winter Wheat":
                    self._draw_wheat(center_x, center_y, crop, game_state.wind_speed)
                else:
                    self._draw_corn(center_x, center_y, crop, game_state.wind_speed)
                    
        # Draw Creatures
        if hasattr(game_state, 'active_spawns'):
            for creature in game_state.active_spawns:
                # Basic validation in case it's a string (old format)
                if hasattr(creature, 'x'):
                    self.draw_creature(creature, dt)

    def draw_machine(self, machine, dt):
        half_w = self.tile_size
        half_h = self.tile_size // 2
        screen_x, screen_y = self.camera.apply(machine.x * half_w, machine.y * half_w)
        
        cx, cy = int(screen_x), int(screen_y)
        
        # Check if we have an asset for this machine
        asset = self.assets.get(machine.type.name)
        if asset:
            # Draw asset centered at bottom
            # Asset width/height
            aw, ah = asset.get_size()
            # Position so bottom center of image is at cx, cy + half_h (bottom of tile)
            # Or center of tile? 
            # Iso tile center is cx, cy. Bottom is cx, cy + half_h.
            # Let's place it at cx - aw/2, cy - ah + half_h
            dest_x = cx - aw // 2
            dest_y = cy - ah + half_h // 2 # Adjust as needed for visual fit
            self.screen.blit(asset, (dest_x, dest_y))
            return

        # Simple shapes for now (Fallback)
        if machine.type.name == "Wind Turbine":
            # Tall pole + rotating blades
            pygame.draw.line(self.screen, (200, 200, 200), (cx, cy), (cx, cy - 60), 4)
            
            import math
            import time
            t = time.time() * 5 # Rotation speed
            
            # 3 Blades
            for i in range(3):
                angle = t + (i * 2 * math.pi / 3)
                bx = cx + math.cos(angle) * 25
                by = (cy - 60) + math.sin(angle) * 25
                pygame.draw.line(self.screen, (255, 255, 255), (cx, cy - 60), (bx, by), 3)
                
        elif machine.type.name == "Solar Panel":
            # Angled rectangle
            # Iso projection of a flat rect
            pts = [
                (cx - 20, cy - 10),
                (cx + 20, cy - 10),
                (cx + 10, cy + 10),
                (cx - 30, cy + 10)
            ]
            pygame.draw.polygon(self.screen, (20, 20, 80), pts) # Dark blue base
            pygame.draw.polygon(self.screen, (50, 50, 200), pts, 0) # Blue panel
            pygame.draw.polygon(self.screen, (200, 200, 255), pts, 1) # Border
            
        elif machine.type.name == "Rain Collector":
            # Funnel shape
            pygame.draw.polygon(self.screen, (100, 100, 100), [(cx-15, cy-30), (cx+15, cy-30), (cx, cy)], 0)
            pygame.draw.rect(self.screen, (80, 80, 80), (cx-5, cy, 10, 10))
            
        elif machine.type.name == "Heater":
            # Red box
            pygame.draw.rect(self.screen, (200, 50, 50), (cx-10, cy-20, 20, 20))

    def draw_harvester(self, grid_x, grid_y, dt):
        half_w = self.tile_size
        screen_x, screen_y = self.camera.apply(grid_x * half_w, grid_y * half_w)
        
        # Check for asset
        asset = self.assets.get('Harvester')
        if asset:
            # Asset width/height
            aw, ah = asset.get_size()
            
            dest_x = int(screen_x) - aw // 2
            dest_y = int(screen_y) - ah + self.tile_size // 2
            
            self.screen.blit(asset, (dest_x, dest_y))
            return
        
        # Draw a futuristic harvester base (Fallback)
        # Base
        pygame.draw.circle(self.screen, (50, 50, 60), (int(screen_x), int(screen_y + 10)), 20)
        pygame.draw.circle(self.screen, (100, 100, 120), (int(screen_x), int(screen_y)), 15)
        
        # Rotating element
        import math
        import time
        t = time.time()
        angle = t * 5
        
        offset_x = math.cos(angle) * 20
        offset_y = math.sin(angle) * 10 # Elliptical rotation
        
        pygame.draw.circle(self.screen, (0, 255, 255), (int(screen_x + offset_x), int(screen_y + offset_y - 20)), 5)
        pygame.draw.circle(self.screen, (0, 255, 255), (int(screen_x - offset_x), int(screen_y - offset_y - 20)), 5)
        
        # Beam
        pygame.draw.line(self.screen, (0, 200, 255), (int(screen_x), int(screen_y - 30)), (int(screen_x), int(screen_y - 100)), 2)

    def _draw_wheat(self, x, y, crop, wind):
        # Check for stage-specific asset first
        stage_asset_key = f'Winter Wheat_stage{min(crop.stage, 2)}'
        asset = self.assets.get(stage_asset_key)
        
        if not asset and crop.stage >= 2:
            # Fall back to main asset for mature crops
            asset = self.assets.get('Winter Wheat')
        
        if asset:
             # Asset width/height
            aw, ah = asset.get_size()
            
            dest_x = x - aw // 2
            dest_y = y - ah + self.tile_size // 2
            
            self.screen.blit(asset, (dest_x, dest_y))
            return

        # Draw multiple stalks (Fallback or early stages)
        # Height depends on stage
        height = 10 + crop.stage * 10
        if height > 40: height = 40
        
        count = 5 + crop.stage * 2
        
        # Wind sway
        import math
        import time
        t = time.time()
        sway = math.sin(t * 2 + x * 0.1) * (wind * 2)
        
        for i in range(count):
            # Random offset within tile
            ox = (i % 3 - 1) * 10
            oy = (i // 3) * 5
            
            start_pos = (x + ox, y + oy)
            end_pos = (x + ox + sway, y + oy - height)
            
            color = (255, 220, 50)
            if crop.state == "Dormant": color = (100, 200, 255)
            elif crop.state == "Dead": color = (100, 100, 100)
            
            pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
            
            # Draw "head"
            if crop.stage >= 2:
                pygame.draw.circle(self.screen, (255, 200, 0), (int(end_pos[0]), int(end_pos[1])), 3)

    def _draw_corn(self, x, y, crop, wind):
        # Check for stage-specific asset first
        stage_asset_key = f'Corn_stage{min(crop.stage, 2)}'
        asset = self.assets.get(stage_asset_key)
        
        if not asset and crop.stage >= 2:
            # Fall back to main asset for mature crops
            asset = self.assets.get('Corn')
        
        if asset:
            # Asset width/height
            aw, ah = asset.get_size()
            
            dest_x = x - aw // 2
            dest_y = y - ah + self.tile_size // 2
            
            self.screen.blit(asset, (dest_x, dest_y))
            return

        # Draw thick stalk (Fallback or early stages)
        height = 15 + crop.stage * 15
        
        import math
        import time
        t = time.time()
        sway = math.sin(t * 1.5 + x * 0.1) * (wind * 1.5)
        
        start_pos = (x, y)
        end_pos = (x + sway, y - height)
        
        color = (100, 200, 50)
        pygame.draw.line(self.screen, color, start_pos, end_pos, 4)
        
        # Leaves
        if crop.stage >= 1:
            # Draw ellipses
            pass
            
    def draw_creature(self, creature, dt):
        half_w = self.tile_size
        screen_x, screen_y = self.camera.apply(creature.x * half_w, creature.y * half_w)
        
        cx, cy = int(screen_x), int(screen_y)
        
        # Bobbing
        import math
        import time
        t = time.time()
        bob = math.sin(t * 3 + creature.x) * 5
        
        asset_name = creature.type.name
        asset = self.assets.get(asset_name)
        
        if asset:
            aw, ah = asset.get_size()
            dest_x = cx - aw // 2
            dest_y = cy - ah + self.tile_size // 2 + int(bob)
            
            self.screen.blit(asset, (dest_x, dest_y))
        else:
            pygame.draw.circle(self.screen, (255, 0, 255), (cx, cy), 10)



    def render_preview(self, grid_x, grid_y, crop_name, valid=True):
        half_w = self.tile_size
        screen_x, screen_y = self.camera.apply(grid_x * half_w, grid_y * half_w)
        
        cx, cy = int(screen_x), int(screen_y)
        
        # Draw highlight tile
        pts = [
            (cx, cy - self.tile_size // 2),
            (cx + self.tile_size, cy),
            (cx, cy + self.tile_size // 2),
            (cx - self.tile_size, cy)
        ]
        
        color = (100, 255, 100, 100) if valid else (255, 100, 100, 100)
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(s, color, pts)
        self.screen.blit(s, (0, 0))
        
        # Draw ghost asset
        asset = self.assets.get(crop_name)
        if asset:
            aw, ah = asset.get_size()
            dest_x = cx - aw // 2
            dest_y = cy - ah + self.tile_size // 2
            
            # Create ghost
            ghost = asset.copy()
            ghost.set_alpha(150)
            self.screen.blit(ghost, (dest_x, dest_y))

    def render_moving_preview(self, grid_x, grid_y, obj, valid=True):
        # Similar to render_preview but takes an object instance
        half_w = self.tile_size
        screen_x, screen_y = self.camera.apply(grid_x * half_w, grid_y * half_w)
        
        cx, cy = int(screen_x), int(screen_y)
        
        # Draw highlight tile
        pts = [
            (cx, cy - self.tile_size // 2),
            (cx + self.tile_size, cy),
            (cx, cy + self.tile_size // 2),
            (cx - self.tile_size, cy)
        ]
        
        color = (100, 255, 255, 100) if valid else (255, 100, 100, 100)
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(s, color, pts)
        self.screen.blit(s, (0, 0))
        
        # Determine asset name
        name = obj.type.name
        if hasattr(obj, 'stage'): # It's a crop
            # Use stage asset if available
            stage_asset_key = f'{name}_stage{min(obj.stage, 2)}'
            if stage_asset_key in self.assets:
                name = stage_asset_key
                
        asset = self.assets.get(name)
        if asset:
            aw, ah = asset.get_size()
            dest_x = cx - aw // 2
            dest_y = cy - ah + self.tile_size // 2
            
            # Create ghost
            ghost = asset.copy()
            ghost.set_alpha(200)
            self.screen.blit(ghost, (dest_x, dest_y))
        else:
            # Fallback for no asset
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 10)
