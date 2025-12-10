import pygame
import os

import math

def remove_white_bg(image_path):
    try:
        img = pygame.image.load(image_path).convert_alpha()
        width, height = img.get_size()
        
        # Create a new surface with alpha channel
        new_img = pygame.Surface((width, height), pygame.SRCALPHA)
        new_img.blit(img, (0, 0))
        
        # Get background color from top-left corner
        # This assumes the corner is part of the background
        bg_ref = new_img.get_at((0, 0))
        
        # Tolerance for "similarity" to background
        # Increased to catch artifacts/shadows near edges
        tolerance = 60 
        
        for x in range(width):
            for y in range(height):
                c = new_img.get_at((x, y))
                
                # Calculate Euclidean distance in RGB space
                dist = math.sqrt((c.r - bg_ref.r)**2 + (c.g - bg_ref.g)**2 + (c.b - bg_ref.b)**2)
                
                if dist < tolerance:
                    new_img.set_at((x, y), (255, 255, 255, 0))
                    
        # Save back
        pygame.image.save(new_img, image_path)
        print(f"Processed {image_path} using bg_ref={bg_ref} and tol={tolerance}")
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def main():
    pygame.init()
    # Set display mode is required for convert_alpha usually, but maybe not for offscreen?
    # Actually convert_alpha needs a display initialized.
    pygame.display.set_mode((100, 100))
    
    asset_dir = "assets"
    files = ["iso_grass_1763665136323.png", "iso_soil_1763665149140.png"]
    
    for f in files:
        path = os.path.join(asset_dir, f)
        if os.path.exists(path):
            remove_white_bg(path)
        else:
            print(f"File not found: {path}")
            
    pygame.quit()

if __name__ == "__main__":
    main()
