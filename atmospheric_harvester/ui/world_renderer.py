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
            self.assets['Wind Turbine_base'] = self.trim_transparent_borders(pygame.image.load(os.path.join(asset_dir, "iso_wind_turbine_base.png")).convert_alpha())
            # Do NOT trim blades to preserve center pivot point (assuming source is centered)
            self.assets['Wind Turbine_blades'] = pygame.image.load(os.path.join(asset_dir, "iso_wind_turbine_blades.png")).convert_alpha()
            self.assets['Rain Collector'] = pygame.image.load(os.path.join(asset_dir, "iso_rain_collector.png")).convert_alpha()
            self.assets['Solar Panel'] = pygame.image.load(os.path.join(asset_dir, "iso_solar_panel.png")).convert_alpha()
            self.assets['Heater'] = pygame.image.load(os.path.join(asset_dir, "iso_heater.png")).convert_alpha()
            self.assets['Battery'] = pygame.image.load(os.path.join(asset_dir, "iso_battery.png")).convert_alpha()
            self.assets['Water Tank'] = pygame.image.load(os.path.join(asset_dir, "iso_single_water_tank.png")).convert_alpha()
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
            
            # Island Base Assets
            self.assets['base_rock'] = pygame.image.load(os.path.join(asset_dir, "iso_island_base_rock.png")).convert_alpha()
            try:
                self.assets['base_bottom'] = pygame.image.load(os.path.join(asset_dir, "iso_island_base_bottom.png")).convert_alpha()
            except:
                self.assets['base_bottom'] = self.assets['base_rock'] # Fallback
            
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
                
            # Scale Island Base Assets
            for key in ['base_rock', 'base_bottom']:
                if key in self.assets and self.assets[key]:
                    img = self.assets[key]
                    aspect = img.get_height() / img.get_width()
                    target_base_h = int(target_w * aspect)
                    self.assets[key] = pygame.transform.scale(img, (target_w, target_base_h))

            # Scale machines to fit tile
            # They should probably be similar width to tiles, maybe a bit narrower/taller
            machine_w = self.tile_size * 1.5
            for key in ['Wind Turbine', 'Rain Collector', 'Solar Panel', 'Heater', 'Battery', 'Sprinkler',
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
                    
            # Custom scaling for Wind Turbine parts (since they are trimmed)
            # Custom scaling for Wind Turbine parts (since they are trimmed)
            if 'Wind Turbine_base' in self.assets:
                img = self.assets['Wind Turbine_base']
                # Scale base by width to match other machines (approx 1.5-1.6 * tile_size)
                target_base_w = int(self.tile_size * 1.6) 
                aspect = img.get_height() / img.get_width()
                target_base_h = int(target_base_w * aspect)
                self.assets['Wind Turbine_base'] = pygame.transform.smoothscale(img, (target_base_w, target_base_h))
                
            if 'Wind Turbine_blades' in self.assets:
                img = self.assets['Wind Turbine_blades']
                # Flip blades horizontally AND vertically 
                img = pygame.transform.flip(img, True, True)
                
                # Scale blades by width (span)
                target_blade_w = int(self.tile_size * 1.6) 
                aspect = img.get_height() / img.get_width()
                target_blade_h = int(target_blade_w * aspect)
                self.assets['Wind Turbine_blades'] = pygame.transform.smoothscale(img, (target_blade_w, target_blade_h))
                
            if 'Water Tank' in self.assets:
                img = self.assets['Water Tank']
                # Scale Water Tank larger to match other buildings
                target_tank_w = int(self.tile_size * 1.7) # Reduced from 1.9
                aspect = img.get_height() / img.get_width()
                target_tank_h = int(target_tank_w * aspect)
                self.assets['Water Tank'] = pygame.transform.smoothscale(img, (target_tank_w, target_tank_h))
                
            if 'Creature Stable' in self.assets:
                img = self.assets['Creature Stable']
                # Scale Creature Stable larger to match other buildings
                target_stable_w = int(self.tile_size * 2.2)
                aspect = img.get_height() / img.get_width()
                target_stable_h = int(target_stable_w * aspect)
                self.assets['Creature Stable'] = pygame.transform.smoothscale(img, (target_stable_w, target_stable_h))
                
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
        depth_layers = 10 # Reduced layer count since each layer will be taller/cleaner
        layer_offset = 24 # Increased offset to show more of the side face (less overlap/ribbing)
        
        base_rock_img = self.assets.get('base_rock')
        base_bottom_img = self.assets.get('base_bottom')
        soil_img = self.assets.get('soil') # Fallback
        grass_img = self.assets.get('grass')
        
        # Determine the "lowest" visible layer for each column to place the tip
        
        for y in range(rows):
            for x in range(cols):
                tile = terrain_map[y][x]
                screen_x, screen_y = self.camera.apply(x * half_w, y * half_w)
                
                # Draw Depth Layers
                # We want a stack of rocks, and the bottom-most one should be the 'tip' if it's the last one for this logical column.
                # But here we are just drawing a generic stack.
                # To make it look like a floating island, we taper it.
                
                max_depth_for_col = depth_layers
                # Taper logic:
                # Distance from center?
                # Simple logic: closer to edge = fewer layers.
                
                # Let's compute a "depth" for this specific x,y
                # Distance from center
                cx, cy = cols / 2, rows / 2
                dist = ((x - cx)**2 + (y - cy)**2)**0.5
                max_dist = (cols**2 + rows**2)**0.5 / 2
                
                # Normalized distance 0..1 (1 is edge)
                norm_dist = dist / max_dist
                
                # Depth decreases as we get closer to edge
                col_depth = int(depth_layers * (1.1 - norm_dist))
                if col_depth < 2: col_depth = 2
                
                # Draw the column
                # Draw from bottom up to avoid overdraw issues if we were doing strict painter's algo, 
                # but for isometric stack downwards, we usually draw top-down or bottom-up?
                # In this loop (y, x), we draw "back to front". 
                # For a single column, we should draw bottom to top? 
                # Actually, standard iso: draw furthest tiles first.
                # Within a tile stack: draw deepest layer first?
                # Yes, deepest layer is 'behind' / 'below'.
                
                dest_x = screen_x - half_w
                
                for d in range(col_depth, 0, -1):
                    # d is layer index from surface down.
                    # so d=col_depth is element at bottom.
                    
                    dy = screen_y + d * layer_offset
                    
                    img_to_draw = base_rock_img if base_rock_img else soil_img
                    
                    # If it is the very bottom layer, use the tip
                    if d == col_depth:
                        if base_bottom_img:
                             img_to_draw = base_bottom_img
                    
                    if img_to_draw:
                        # Center the image? 
                        # Assumes images are scaled to target_w wide.
                        # target_w is tile_size * 2 (full width of iso tile)
                        # We blit at dest_x which is screen_x - half_w.
                        # screen_x is CENTER of tile. half_w is dist to left edge.
                        # So dest_x is LEFT edge of tile sprite box.
                        # This seems correct for standard iso tile blitting if sprite is WxH.
                        
                        # However, for 'tip' or varying heights, we might need to adjust y.
                        # If the tip image is tall, we need to adjust.
                        
                        iw, ih = img_to_draw.get_size()
                        # We want the 'top surface' of this block to align with dy.
                        # For a standard block, top surface center is at some offset?
                        # Let's assume the sprite is a cube.
                        # We just blit it at dy?
                        
                        # Adjust for image height.
                        # Usually for a tile at screen_y, we blit at screen_y - height_correction.
                        # But here dy describes the logical center/base?
                        # Let's revert to simple stacking:
                        # blit(img, (dest_x, dy)) assumes top-left of image is at dest_x, dy.
                        # This places the image *below* the previous one.
                        
                        # Let's try to center it vertically based on image properties?
                        # No, just pile them.
                        
                        self.screen.blit(img_to_draw, (dest_x, dy))
                
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
            self.draw_machine(machine, dt, game_state.wind_speed)

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

    def draw_machine(self, machine, dt, wind_speed=0):
        half_w = self.tile_size
        half_h = self.tile_size // 2
        screen_x, screen_y = self.camera.apply(machine.x * half_w, machine.y * half_w)
        
        cx, cy = int(screen_x), int(screen_y)
        
        # Check if we have an asset for this machine
        asset = self.assets.get(machine.type.name)
        if asset and machine.type.name != "Wind Turbine": # Special handling for Turbine
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
            
            # Special FX for Heater
            if machine.type.name == "Heater" and machine.active:
                import math, time
                t = time.time()
                
                # Center point for effects approx at mid-height of asset
                glow_cx = cx
                # Adjust vertical center based on asset look (assuming core is middle-ish)
                glow_cy = dest_y + ah // 2 

                # 1. Pulsing Core
                pulse = (math.sin(t * 5) + 1) / 2 # 0..1
                radius = int(self.tile_size * 0.4 + pulse * 5)
                
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                # Red color with alpha pulsing - VERY LOW ALPHA
                alpha = int(20 + pulse * 40)
                pygame.draw.circle(glow_surf, (255, 50, 0, alpha), (radius, radius), radius)
                self.screen.blit(glow_surf, (glow_cx - radius, glow_cy - radius), special_flags=pygame.BLEND_ADD)
                
                # 2. Rising Embers (Stateless)
                for i in range(5):
                    # Deterministic pseudo-random based on ID and time
                    seed = i * 13.0
                    cycle_len = 2.0
                    local_t = (t + seed) % cycle_len
                    norm_t = local_t / cycle_len # 0..1 progress
                    
                    # Wiggle up
                    ex = glow_cx + math.sin(t * 3 + seed) * 10
                    # Start low, rise high
                    ey = glow_cy + 10 - (norm_t * 50) 
                    
                    # Fade out - VERY LOW MAX ALPHA
                    e_alpha = int(120 * (1.0 - norm_t))
                    if e_alpha > 0:
                        ember_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                        pygame.draw.circle(ember_surf, (255, 200, 100, e_alpha), (3, 3), 2)
                        self.screen.blit(ember_surf, (int(ex)-3, int(ey)-3), special_flags=pygame.BLEND_ADD)

            # Special FX for Battery
            if machine.type.name == "Battery" and machine.active:
                import math, time
                t = time.time()
                
                glow_cx = cx
                glow_cy = dest_y + ah // 2 

                # 1. Pulsing Blue Core - REMOVED 
                # pulse = (math.sin(t * 3) + 1) / 2 
                # radius = int(self.tile_size * 0.4 + pulse * 3)
                # glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                # alpha = int(15 + pulse * 35)
                # pygame.draw.circle(glow_surf, (0, 150, 255, alpha), (radius, radius), radius)
                # self.screen.blit(glow_surf, (glow_cx - radius, glow_cy - radius), special_flags=pygame.BLEND_ADD)
                
                # 2. Rising Energy Motes
                for i in range(4):
                    seed = i * 7.0
                    cycle_len = 2.5
                    local_t = (t + seed) % cycle_len
                    norm_t = local_t / cycle_len
                    
                    # Vertical rise with slight jitter
                    ex = glow_cx + math.sin(t * 10 + seed) * 3 
                    ey = glow_cy + 15 - (norm_t * 40)
                    
                    # VERY LOW MAX ALPHA
                    e_alpha = int(120 * (1.0 - norm_t))
                    if e_alpha > 0:
                        spark_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                        pygame.draw.circle(spark_surf, (100, 200, 255, e_alpha), (2, 2), 2)
                        self.screen.blit(spark_surf, (int(ex)-2, int(ey)-2), special_flags=pygame.BLEND_ADD)

            # Special FX for Rain Collector
            if machine.type.name == "Rain Collector" and machine.active:
                import math, time
                t = time.time()
                
                # Funnel dimensions roughly
                funnel_top_y = dest_y + 5
                funnel_bottom_y = dest_y + ah * 0.5 
                
                # Render more, smaller, faster drops
                for i in range(10):
                    seed = i * 123.45
                    cycle_len = 0.8 # Faster cycle
                    local_t = (t + seed) % cycle_len
                    norm_t = local_t / cycle_len
                    
                    # Randomize X within funnel width (approx 30px wide?)
                    # Deterministic randomness
                    x_seed = (seed * 997) % 30 - 15 
                    
                    dx = cx + x_seed
                    # Start higher to fall IN
                    dy = funnel_top_y - 15 + (norm_t * 40) 
                    
                    # Only draw if within vertical bounds of 'falling in'
                    if dy < funnel_bottom_y:
                        # Drop is a small vertical streak
                        drop_surf = pygame.Surface((2, 5), pygame.SRCALPHA)
                        alpha = int(200 * (1.0 - norm_t)) if norm_t > 0.5 else 200
                        # Light blue streak
                        pygame.draw.line(drop_surf, (200, 230, 255, alpha), (1, 0), (1, 4), 2)
                        self.screen.blit(drop_surf, (int(dx)-1, int(dy)), special_flags=pygame.BLEND_ADD)

            # Special FX for Water Tank
            if machine.type.name == "Water Tank":
                import math, time
                t = time.time()
                
                # Bubbles rising
                tank_cx = cx
                # Adjust vertical range - shift UP slightly
                tank_bottom_y = dest_y + ah * 0.77 # Was 0.82
                tank_top_y = dest_y + ah * 0.50 # Was 0.55 
                
                for i in range(8):
                    seed = i * 44.0
                    cycle_len = 3.0 # Slow rise
                    local_t = (t + seed) % cycle_len
                    norm_t = local_t / cycle_len
                    
                    # Wiggle - wider to fill the tank
                    bx = tank_cx + math.sin(t * 2 + seed) * 4 + ((seed * 100) % 20 - 10) # +/- 10px offset
                    by = tank_bottom_y - (norm_t * (tank_bottom_y - tank_top_y))
                    
                    # Fade in then out (sin wave 0..PI)
                    b_alpha = int(120 * math.sin(norm_t * 3.14159)) 
                    if b_alpha > 0:
                        # Make bigger surface for better bubble
                        bubble_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                        
                        # outline circle
                        pygame.draw.circle(bubble_surf, (200, 240, 255, b_alpha), (3, 3), 2, 1) 
                        
                        # little shine (highlight)
                        shine_alpha = int(b_alpha * 1.5) if b_alpha * 1.5 < 255 else 255
                        pygame.draw.circle(bubble_surf, (255, 255, 255, shine_alpha), (4, 2), 1)
                        
                        self.screen.blit(bubble_surf, (int(bx)-3, int(by)-3), special_flags=pygame.BLEND_ADD)

            return

        # Simple shapes for now (Fallback)
        if machine.type.name == "Wind Turbine":
            # Check for base and blades assets
            base_asset = self.assets.get('Wind Turbine_base')
            blades_asset = self.assets.get('Wind Turbine_blades')
            
            if base_asset and blades_asset:
                # Draw Base
                bw, bh = base_asset.get_size()
                base_x = cx - bw // 2
                base_y = cy - bh + half_h // 2
                self.screen.blit(base_asset, (base_x, base_y))
                
                # Draw Blades
                if hasattr(machine, 'animation_offset'):
                     # Calculate rotation angle
                     import time
                     
                     # wind_speed ranges ~0-20 m/s usually? 
                     # Rotation speed:
                     # Always rotate for now to ensure visibility
                     # Use modulo 360 to prevent huge number issues
                     rotation_speed = 120.0 # Slower, clearer speed
                     angle = ((time.time() + machine.animation_offset) * rotation_speed) % 360
                     
                     # Rotate blades
                     # Ideally we rotate around the center of the image.
                     rotated_blades = pygame.transform.rotate(blades_asset, -angle) # Negative for clockwise?
                     
                     # Blit center
                     # We need to know where the "hub" is relative to the base.
                     # Assuming blades asset is centered on hub.
                     # Assuming base hub is at top center?
                     # Let's guess: blade center should be at top of base + offset
                     # Since we trimmed the base, the top pixel is the top of the tower/structure.
                     hub_x = cx
                     hub_y = base_y + int(bh * 0.08) # Pivot higher (8% down) - moving UP 'a little bit more'
                     
                     rw, rh = rotated_blades.get_size()
                     self.screen.blit(rotated_blades, (hub_x - rw // 2, hub_y - rh // 2))
                     
            else:
                # Fallback drawing
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
